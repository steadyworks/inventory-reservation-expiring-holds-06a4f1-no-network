# Inventory Reservation with Expiring Holds

Build a product reservation system — like buying limited-edition sneakers or concert tickets — where stock is finite, holds are temporary, and checkout is final. Users compete for limited units in real time.

## Stack

- **Frontend**: Pure React, port **3000**
- **Backend**: Django, port **3001**
- **Persistence**: MySQL at port **3306**, schema name `inventory`
- **Real-time**: WebSockets

## User Identity

When a user first visits the site, they are prompted to enter a display name. This name is stored in the browser session and persists across page reloads in the same tab/session. The display name is shown on screen at all times and is used to associate holds and orders with a specific user. No authentication is required — the name is the identity.

## The App

The app is a **single page at `/`** with two sections visible simultaneously: an **Admin Panel** and a **Shop View**. Both are always present on the page.

---

## Admin Panel

The admin panel lets you seed the catalog. From here you can add new products. Each product entry requires:

- A **name** (text)
- An **image URL** (optional — if omitted, show a placeholder)
- An **initial stock quantity** (positive integer)

Once a product is added, it appears in both the admin panel list and the shop view immediately. Products persist across reloads.

A **Reset All** button wipes all products, active holds, and confirmed orders, returning the system to a blank state.

---

## Shop View

The shop displays all products currently in the catalog. For each product, show:

- The product name and image (or placeholder)
- The **available quantity**: total stock minus all active (non-expired) holds minus all confirmed orders
- A **Reserve** button, enabled only when available quantity is greater than zero and the current user does not already hold that item

Available quantities must reflect the live state — when another user reserves or releases a unit, the number updates without requiring a page reload.

---

## Reservation (Hold) Flow

Clicking **Reserve** on a product creates a temporary hold for 1 unit, attributed to the current user.

- A hold lasts **90 seconds**. Once it expires, the unit is automatically returned to available stock and the hold disappears from the cart.
- While a hold is active, that unit is subtracted from the available quantity visible to **all** users.
- A user may hold at most **3 items total** across all products simultaneously. Attempting to reserve a fourth item while already holding three must produce a visible error message.
- The user may release a hold early by clicking **Release** on that item in the cart.
- Each user can hold at most 1 unit of a given product at a time.

---

## Cart

A **Cart** section shows the current user's active holds. For each held item, display:

- Product name
- A live **countdown timer** showing the seconds remaining on the hold
- A **Release** button to return the unit early

When a hold expires, it is automatically removed from the cart and the unit is returned to available stock for everyone.

---

## Checkout Flow

A **Checkout** button converts all active holds in the cart into confirmed orders in a single action.

- Confirmed orders permanently reduce the product's stock — they never expire and cannot be released.
- After checkout, the cart is emptied.
- Confirmed orders appear in an **Order History** section. Multiple checkouts each produce a separate order entry.
- Order history and confirmed orders persist across page reloads.

---

## Real-Time Updates

All connected clients must stay in sync without polling:

- When any user reserves, releases, or checks out, the **available quantity** for affected products updates live for every connected session.
- A live **connected user count** is displayed on the page at all times.

---

## Persistence

On page reload:

- All products remain in the catalog.
- Active holds that have not yet expired are restored with their remaining time intact — the countdown continues from where it left off, not restarted from 90 seconds.
- Expired holds are cleaned up automatically on load.
- Confirmed orders remain in order history.

---

## Concurrency

If two users simultaneously attempt to reserve the last available unit of a product, exactly one must succeed. The other must receive a clear failure response (error message or updated "out of stock" display). The system must not allow the available quantity to go negative.

---

## `data-testid` Reference

Every interactive and observable element must carry the exact `data-testid` below. The test harness depends on these strings.

### Global

- `user-count` — live count of connected users
- `reset-all-btn` — the Reset All button

### Admin Panel

- `admin-panel` — the admin panel container
- `product-name-input` — text input for the product name
- `product-image-input` — text input for the image URL
- `product-stock-input` — number input for initial stock quantity
- `add-product-btn` — button that submits the new product form
- `product-{id}` — each product row in the admin list, where `{id}` is the product's unique identifier

### Shop View

- `shop-view` — the shop container
- `shop-product-{id}` — each product card in the shop
- `available-qty-{id}` — the available quantity display for a product
- `reserve-btn-{id}` — the Reserve button for a product

### Cart

- `cart` — the cart container
- `hold-timer-{productId}` — the countdown timer (in seconds) for a held item
- `release-{productId}` — the Release button for a held item
- `checkout-btn` — the Checkout button

### Order History

- `order-history` — the order history container
- `order-{orderId}` — each order entry in history
