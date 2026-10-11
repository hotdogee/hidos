# Payments: design note (#9, #10, #11)

Not implemented. Payments need business decisions that the code can't make:
what is sold (analyses, storage, subscriptions), the prices, the payment
provider and the legal entity, invoicing and tax for the target countries,
and refunds. This note records a design that fits the existing code, so the
work can start once those decisions are made.

## Architecture (#11)

* **Provider**: use a hosted checkout from a payment provider (for example
  Stripe Checkout, or a Taiwanese provider such as ECPay if invoicing must be
  local). Cell Cloud never handles card data; that keeps PCI scope minimal.
* **Model**: a new `billing` app with
  * `Plan`: name, price, period, quota (analyses per month, storage bytes)
  * `Subscription`: user, plan, provider customer and subscription ids,
    status, current period end
  * `Credit`: user, amount, reason, for pay-per-analysis
  * `PaymentEvent`: raw webhook payloads, stored for auditing
* **Enforcement**: one check in `cell.api.TaskViewSet.perform_create`. It sits
  next to the existing rate limit (#26) and the duplicate upload logic, and
  refuses a submission (HTTP 402) when the user has no quota left. Storage
  quota is checked in the same place and in `fs.uploads`.
* **Webhooks**: `POST /api/v1/billing/webhook` verifies the provider's
  signature, stores the event, and updates `Subscription` and `Credit`
  idempotently (keyed by event id).

## Backend (#9)

* the models and migrations above
* checkout session creation (`POST /api/v1/billing/checkout {plan}`) that
  returns the provider's checkout URL
* the webhook endpoint, and a management command to re-sync subscriptions
  from the provider
* quota checks and a usage endpoint (`GET /api/v1/billing/usage`)
* admin views for plans, subscriptions and manual credits

## Frontend (#10)

In the single page app: a plans page, a redirect to checkout, a billing and
usage page, and a clear message when a submission is refused for quota.
