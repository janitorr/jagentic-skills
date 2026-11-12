# orders

## Purpose

Serve order listings to the storefront and partner portal.

## Requirements

### Requirement: Order listing

The service SHALL return the caller's order listings at `GET /orders`.

#### Scenario: Empty order list

- **WHEN** the caller requests `GET /orders` and has no orders
- **THEN** the service returns `200` with an empty list
