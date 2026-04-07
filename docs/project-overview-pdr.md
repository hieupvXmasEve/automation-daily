# Product Development Requirements

## Problem

Ops needs a terminal tool to verify whether Shopee order exports and printed shipping labels align before downstream handling.

## Users

- Warehouse staff
- Operations staff
- Shop owner/admin

## Inputs

- Shopee Excel export
- Shipping label PDF

## Outputs

- CSV comparison report
- Excel workbook report
- PDF printable report

## Functional Requirements

- Run locally from terminal
- Accept explicit file paths
- Compare orders by order id
- Highlight missing and mismatched orders
- Export reports to a chosen directory

## Non-Functional Requirements

- Offline-friendly
- No GUI required
- Clear error messages
- Deterministic output for the same input

## V1 Out Of Scope

- OCR
- GUI/TUI
- Multiple marketplace support
- Direct Shopee API integration
