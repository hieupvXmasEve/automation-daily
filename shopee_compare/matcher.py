from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher

from .models import ComparisonRecord, ExcelOrder, OrderItem, PdfItem, PdfOrder
from .utils import join_notes, safe_compare, text_tokens, token_set_with_adjacent


VALID_STATUSES = ("matched", "mismatch", "missing-in-excel", "missing-in-pdf")
CONFIDENT_MATCH_THRESHOLD = 0.93
AMBIGUOUS_GAP_THRESHOLD = 0.02
CONTENT_TOKEN_COVERAGE_THRESHOLD = 0.90


def compare_orders(
    excel_orders: list[ExcelOrder],
    pdf_orders: list[PdfOrder],
) -> tuple[list[ComparisonRecord], dict[str, int]]:
    excel_map = {order.order_id: order for order in excel_orders}
    pdf_map = {order.order_id: order for order in pdf_orders}

    counts: Counter[str] = Counter()
    comparisons: list[ComparisonRecord] = []

    for order_id in sorted(set(excel_map) | set(pdf_map)):
        excel_order = excel_map.get(order_id)
        pdf_order = pdf_map.get(order_id)

        if excel_order and pdf_order:
            notes: list[str] = []
            waybill_match = safe_compare(excel_order.waybill, pdf_order.waybill)
            datetime_match = safe_compare(excel_order.order_datetime, pdf_order.order_datetime)
            item_result = _compare_items(excel_order.items, pdf_order.items)
            quantity_match = (
                excel_order.total_quantity == pdf_order.total_quantity == item_result["pdf_visible_quantity"]
                if pdf_order.total_quantity is not None
                else excel_order.total_quantity == item_result["pdf_visible_quantity"]
            )

            if not pdf_order.template_ok:
                notes.append(f"pdf template requires review: {'; '.join(pdf_order.template_issues)}")
            if waybill_match is False:
                notes.append("waybill mismatch")
            if datetime_match is False:
                notes.append("order datetime mismatch")
            if quantity_match is False:
                notes.append("quantity mismatch")
            if pdf_order.total_quantity is not None and pdf_order.total_quantity != item_result["pdf_visible_quantity"]:
                notes.append(
                    f"visible item quantity {item_result['pdf_visible_quantity']} differs from PDF header {pdf_order.total_quantity}"
                )
            if item_result["missing_excel_items"]:
                notes.append(f"missing items in PDF: {item_result['missing_excel_items']}")
            if item_result["unclear_pdf_items"]:
                notes.append(f"unclear PDF items: {item_result['unclear_pdf_items']}")

            status = "mismatch" if notes else "matched"
            counts[status] += 1
            comparisons.append(
                ComparisonRecord(
                    order_id=order_id,
                    status=status,
                    notes=join_notes(notes),
                    excel_waybill=excel_order.waybill,
                    pdf_waybill=pdf_order.waybill,
                    waybill_match=waybill_match,
                    excel_order_datetime=excel_order.order_datetime,
                    pdf_order_datetime=pdf_order.order_datetime,
                    datetime_match=datetime_match,
                    excel_total_quantity=excel_order.total_quantity,
                    pdf_total_quantity=pdf_order.total_quantity,
                    quantity_match=quantity_match,
                    item_match_status=item_result["item_match_status"],
                    pdf_template_ok=pdf_order.template_ok,
                    pdf_template_issues="; ".join(pdf_order.template_issues),
                    expected_item_count=len(excel_order.items),
                    pdf_visible_item_count=len(pdf_order.items),
                    pdf_visible_quantity=item_result["pdf_visible_quantity"],
                    missing_excel_items=item_result["missing_excel_items"],
                    unclear_pdf_items=item_result["unclear_pdf_items"],
                    excel_status=excel_order.order_status,
                    excel_recipient_name=excel_order.recipient_name,
                    pdf_recipient_name=pdf_order.recipient_name,
                    pdf_page_number=pdf_order.page_number,
                    excel_item_summary=excel_order.item_summary,
                    pdf_item_summary=pdf_order.item_summary,
                )
            )
            continue

        if excel_order:
            counts["missing-in-pdf"] += 1
            comparisons.append(
                ComparisonRecord(
                    order_id=order_id,
                    status="missing-in-pdf",
                    notes="order exists in Excel only",
                    excel_waybill=excel_order.waybill,
                    pdf_waybill=None,
                    waybill_match=None,
                    excel_order_datetime=excel_order.order_datetime,
                    pdf_order_datetime=None,
                    datetime_match=None,
                    excel_total_quantity=excel_order.total_quantity,
                    pdf_total_quantity=None,
                    quantity_match=None,
                    item_match_status="missing-pdf-order",
                    pdf_template_ok=None,
                    pdf_template_issues="",
                    expected_item_count=len(excel_order.items),
                    pdf_visible_item_count=None,
                    pdf_visible_quantity=None,
                    missing_excel_items="\n".join(item.missing_summary() for item in excel_order.items),
                    unclear_pdf_items="",
                    excel_status=excel_order.order_status,
                    excel_recipient_name=excel_order.recipient_name,
                    pdf_recipient_name=None,
                    pdf_page_number=None,
                    excel_item_summary=excel_order.item_summary,
                    pdf_item_summary=None,
                )
            )
            continue

        pdf_order = pdf_map[order_id]
        counts["missing-in-excel"] += 1
        comparisons.append(
            ComparisonRecord(
                order_id=order_id,
                status="missing-in-excel",
                notes="order exists in PDF only",
                excel_waybill=None,
                pdf_waybill=pdf_order.waybill,
                waybill_match=None,
                excel_order_datetime=None,
                pdf_order_datetime=pdf_order.order_datetime,
                datetime_match=None,
                excel_total_quantity=None,
                pdf_total_quantity=pdf_order.total_quantity,
                quantity_match=None,
                item_match_status="missing-excel-order",
                pdf_template_ok=pdf_order.template_ok,
                pdf_template_issues="; ".join(pdf_order.template_issues),
                expected_item_count=None,
                pdf_visible_item_count=len(pdf_order.items),
                pdf_visible_quantity=sum(item.quantity for item in pdf_order.items),
                missing_excel_items="",
                unclear_pdf_items=pdf_order.item_summary,
                excel_status=None,
                excel_recipient_name=None,
                pdf_recipient_name=pdf_order.recipient_name,
                pdf_page_number=pdf_order.page_number,
                excel_item_summary=None,
                pdf_item_summary=pdf_order.item_summary,
            )
        )

    summary = {
        "excel_orders": len(excel_orders),
        "pdf_orders": len(pdf_orders),
        "matched": counts["matched"],
        "mismatch": counts["mismatch"],
        "missing_in_excel": counts["missing-in-excel"],
        "missing_in_pdf": counts["missing-in-pdf"],
        "total_compared": len(comparisons),
    }
    return comparisons, summary


def _compare_items(excel_items: list[OrderItem], pdf_items: list[PdfItem]) -> dict[str, object]:
    remaining = [item.quantity for item in excel_items]
    missing_items: list[str] = []
    unclear_pdf_items: list[str] = []
    pdf_visible_quantity = sum(item.quantity for item in pdf_items)

    for pdf_item in pdf_items:
        if pdf_item.layout_clipped:
            unclear_pdf_items.append(pdf_item.summary())
            continue

        best_index = None
        best_score = 0.0
        second_score = 0.0
        for index, excel_item in enumerate(excel_items):
            score = _item_similarity(excel_item, pdf_item)
            if score > best_score:
                second_score = best_score
                best_score = score
                best_index = index
            elif score > second_score:
                second_score = score

        if best_index is None:
            unclear_pdf_items.append(pdf_item.summary())
            continue

        if best_score < CONFIDENT_MATCH_THRESHOLD or best_score - second_score < AMBIGUOUS_GAP_THRESHOLD:
            unclear_pdf_items.append(pdf_item.summary())
            continue

        coverage = _item_token_coverage(excel_items[best_index], pdf_item)
        if coverage < CONTENT_TOKEN_COVERAGE_THRESHOLD:
            unclear_pdf_items.append(pdf_item.summary())
            continue

        remaining[best_index] = max(0, remaining[best_index] - pdf_item.quantity)

    for excel_item, missing_quantity in zip(excel_items, remaining):
        if missing_quantity > 0:
            missing_items.append(
                OrderItem(
                    name=excel_item.name,
                    sku=excel_item.sku,
                    variant=excel_item.variant,
                    quantity=missing_quantity,
                ).missing_summary()
            )

    item_match_status = "complete"
    if missing_items and unclear_pdf_items:
        item_match_status = "partial-and-unclear"
    elif missing_items:
        item_match_status = "partial"
    elif unclear_pdf_items:
        item_match_status = "unclear"

    return {
        "item_match_status": item_match_status,
        "missing_excel_items": "\n".join(missing_items),
        "unclear_pdf_items": " | ".join(unclear_pdf_items),
        "pdf_visible_quantity": pdf_visible_quantity,
    }


def _item_similarity(excel_item: OrderItem, pdf_item: PdfItem) -> float:
    pdf_key = pdf_item.match_key()
    combined_score = SequenceMatcher(None, excel_item.match_key(), pdf_key).ratio()
    name_score = SequenceMatcher(None, excel_item.name_key(), pdf_key).ratio()
    variant_key = excel_item.variant_key()
    if variant_key:
        variant_score = 1.0 if variant_key in pdf_key else SequenceMatcher(None, variant_key, pdf_key).ratio()
    else:
        variant_score = 1.0
    quantity_score = 1.0 if pdf_item.quantity == excel_item.quantity else 0.0
    return (combined_score * 0.45) + (name_score * 0.2) + (variant_score * 0.3) + (quantity_score * 0.05)


def _item_token_coverage(excel_item: OrderItem, pdf_item: PdfItem) -> float:
    expected_tokens = [
        token
        for token in text_tokens(excel_item.match_text())
        if len(token) >= 3 or any(character.isdigit() for character in token)
    ]
    visible_tokens = token_set_with_adjacent(pdf_item.raw_text)
    if not expected_tokens:
        return 1.0
    matched = sum(1 for token in expected_tokens if token in visible_tokens)
    return matched / len(expected_tokens)
