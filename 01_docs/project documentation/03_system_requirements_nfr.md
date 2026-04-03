## 1. Performance Requirements

These ensure the application responds quickly to user actions.

| ID | Requirement |
| --- | --- |
| NFR-P1 | The mobile application must load the menu within **2 seconds** under normal network conditions |
| NFR-P2 | The backend API must respond to requests within **500 milliseconds** |
| NFR-P3 | The system must support **at least 100 concurrent users** during peak hours |
| NFR-P4 | Order placement requests must be processed within **3 seconds** |

---

# 2. Availability and Reliability

These ensure the system remains operational.

| ID | Requirement |
| --- | --- |
| NFR-A1 | The system must maintain **99% uptime** |
| NFR-A2 | Orders must never be lost during system interruptions |
| NFR-A3 | The system must automatically retry failed transactions |
| NFR-A4 | The system must maintain order records even after app restarts |

---

# 3. Security Requirements

Security is critical because the system handles **payments and personal data**.

| ID | Requirement |
| --- | --- |
| NFR-S1 | All communication between app and server must use **HTTPS encryption** |
| NFR-S2 | User passwords must be stored using **secure hashing algorithms** |
| NFR-S3 | Only authorized admins can access the restaurant dashboard |
| NFR-S4 | Payment transactions must be validated before confirming orders |
| NFR-S5 | The system must protect against common web attacks (SQL injection, authentication attacks) |

---

# 4. Usability Requirements

These ensure the application is easy to use for customers and restaurant staff.

| ID | Requirement |
| --- | --- |
| NFR-U1 | The app interface must be intuitive and easy to navigate |
| NFR-U2 | New users must be able to place an order within **3 minutes of first use** |
| NFR-U3 | The ordering process must require **no more than 5 steps** |
| NFR-U4 | The admin dashboard must display incoming orders clearly |

---

# 5. Scalability Requirements

These allow the system to grow if more restaurants are added.

| ID | Requirement |
| --- | --- |
| NFR-SC1 | The backend architecture must support horizontal scaling |
| NFR-SC2 | The system must allow onboarding of additional restaurants in future versions |
| NFR-SC3 | The database must handle increasing order volumes without performance degradation |

---

# 6. Maintainability

These requirements help developers maintain the system.

| ID | Requirement |
| --- | --- |
| NFR-M1 | The system must follow modular architecture principles |
| NFR-M2 | All APIs must be documented |
| NFR-M3 | Code must be version controlled using Git |
| NFR-M4 | The system must support automated deployment pipelines |

---

# 7. Compatibility

These ensure the application works across devices.

| ID | Requirement |
| --- | --- |
| NFR-C1 | The mobile app must support Android devices running Android 8 and IOS devices |
| NFR-C2 | The backend must support modern REST API standards |
| NFR-C3 | The system must work on both WiFi and mobile networks |

---

# 8. Data Integrity

These requirements protect the accuracy of system data.

| ID | Requirement |
| --- | --- |
| NFR-D1 | Each order must have a unique identifier |
| NFR-D2 | Payment records must match order records |
| NFR-D3 | The system must prevent duplicate orders during payment processing |