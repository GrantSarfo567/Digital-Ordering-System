# Functional Requirements (Expanded)

## 1. Customer Functional Requirements

These describe what the **end-user of the mobile app** can do.

| ID | Requirement |
| --- | --- |
| FR1 | Users must be able to register an account |
| FR2 | Users must be able to log in and log out |
| FR3 | Users must be able to browse the restaurant menu |
| FR4 | Users must be able to view food item details |
| FR5 | Users must be able to add items to cart |
| FR6 | Users must be able to remove items from cart |
| FR7 | Users must be able to modify item quantity |
| FR8 | Users must be able to place an order |
| FR9 | Users must be able to choose payment method |
| FR10 | Users must be able to pay via Mobile Money |
| FR11 | Users must receive confirmation when order is placed |
| FR12 | Users must be able to view order status |
| FR13 | Users must view order history |
| FR14 | Users must be able to cancel an order before preparation |
| FR15 | Users must be able to save delivery location |
| fR16 | Users must be able to get a refund when orders are insufficient |

# Restaurant Admin Functional Requirements (Operational Only)

These requirements define what the **restaurant staff can do inside the application**, focusing only on **order processing and fulfillment**.

| ID | Requirement |
| --- | --- |
| FR-RA1 | Admin must be able to securely log into the restaurant dashboard |
| FR-RA2 | Admin must be able to view all incoming customer orders |
| FR-RA3 | Admin must receive real-time notifications when a new order is placed |
| FR-RA4 | Admin must be able to view detailed order information (items, quantities, customer location, payment status) |
| FR-RA5 | Admin must be able to accept an order for preparation |
| FR-RA6 | Admin must be able to reject an order if it cannot be fulfilled |
| FR-RA7 | Admin must be able to update order status (Preparing → Ready for Delivery → Completed) |
| FR-RA8 | Admin must be able to view a list of active orders |
| FR-RA9 | Admin must be able to view completed orders |
| FR-RA10 | Admin must be able to view payment confirmation for each order |

# 3. Delivery Rider Functional Requirements (Optional for MVP) - Later

If you include riders in the system.

| ID | Requirement |
| --- | --- |
| FR28 | Rider must be able to log in |
| FR29 | Rider must view assigned deliveries |
| FR30 | Rider must update delivery status |
| FR31 | Rider must confirm delivery completion |
| FR32 | Rider must view delivery history |

# 4. System-Level Functional Requirements - Top Priority

These are **background system operations**.

| ID | Requirement |
| --- | --- |
| FR33 | System must process payment transactions |
| FR34 | System must generate order IDs |
| FR35 | System must store order records |
| FR36 | System must notify restaurant when order arrives |
| FR37 | System must notify customer when order status changes |
| FR38 | System must record payment confirmations |