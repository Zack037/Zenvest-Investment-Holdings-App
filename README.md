# Zenvest Investment Holdings v26 — Complete Public Website + Protected Portal

This version improves the public website so it looks complete for visitors before login.

## Main public website improvements

- Public homepage with service-portal layout.
- Public navigation: Home, Investments, Products, Performance, About, Support, Sign in, Register.
- Public investment rate section now shows demo percentage profit ranges instead of placeholder text.
- Demo sample rates include:
  - Starter Growth: 8%–12%
  - Balanced Project: 13%–18%
  - Expansion Project: 19%–25%
- Public pages include a clear investment process flow:
  1. View opportunity
  2. Register or login
  3. Accept project
  4. Submit payment details
  5. Admin verifies
  6. Track performance
- Public performance page shows sample funding/profit/loss style information.
- Public product, investment, performance, support, login, and register sections are accessible without login.
- Confidential actions remain protected behind login.

## Protected features retained

- Member registration and approval.
- Username or email login.
- Admin/member refresh-safe navigation.
- Admin member controls.
- Investment acceptance and payment submission.
- Editable/deletable investment records.
- Completed/passed project archive and performance tracking.
- Simple support chatbot and staff/member message inbox.
- Reports, settings, products, projects, milestones, and contacts.

## Login details

Chairman:
- username: chairman
- password: chairman123

Manager:
- username: manager
- password: manager123

Secretary:
- username: secretary
- password: secretary123

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```


## v28 public support and roles update

- Staff roles are Chairman, Manager, and Secretary.
- Default Chairman login: `chairman / chairman123`.
- The Chairman can choose which staff account acts as Customer Support.
- Only the selected Customer Support admin can reply to public/member chat messages.
- Public visitors can send enquiries before login from the Support page.
- Members can also chat after login.
- Public investment rates show demo percentage profit examples such as Starter 8%–12%, Balanced 13%–18%, and Expansion 19%–25%.
- Confidential investment acceptance, payment receipts, private member records, and admin controls still require login.

## v29 member-role and enter-to-send chat improvement

- Added a business-facing member role/category field, separate from system access role.
- Member role/category options include Standard Member, Investment Member, Premium Investor, VIP Investor, Project Partner, Prospective Member, and Dormant / Monitoring.
- The Members page now has a dedicated **Assign member role** tab with filters and one-click common assignments.
- Pending member approval now lets staff assign the member role/category before approving.
- Manual member creation now includes member role/category selection.
- Member edit controls now include role/category, status, details, and password reset in one place.
- Public, member, and admin chat now use the Enter message bar as the main send method.
- Removed the extra backup chat forms that created too many clicks and confusion.
