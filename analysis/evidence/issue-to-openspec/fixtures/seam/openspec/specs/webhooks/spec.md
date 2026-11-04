# webhooks Specification

## Purpose

Deliver partner events to the configured webhook endpoint.

## Requirements

### Requirement: Deliver an event to the partner endpoint
The system SHALL POST the event payload to the configured endpoint and SHALL report
the outcome to the caller.

#### Scenario: Successful delivery
- **WHEN** the endpoint accepts the event
- **THEN** the caller receives the response status

#### Scenario: Failed delivery
- **WHEN** the endpoint rejects the event
- **THEN** the caller receives an error
