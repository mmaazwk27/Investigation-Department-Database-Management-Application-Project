# 🕵️ Investigation Department Database Management System 
# (Crime and Criminal Database Management System

A robust web-based Crime & Investigation Management System designed for administrative control and efficient handling of police, criminal, case, and evidence data. Built with **Flask** and **SQLAlchemy**, this project is developed as part of a **DBMS university coursework**, incorporating **role-based access**, relational data integrity, and a modern UI.

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)&nbsp;
![Flask](https://img.shields.io/badge/Flask-Web_Framework-000000?style=for-the-badge&logo=flask&logoColor=white)&nbsp;
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-FCA121?style=for-the-badge&logo=sqlalchemy&logoColor=white)&nbsp;
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)&nbsp;
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)&nbsp;

![HTML5](https://img.shields.io/badge/HTML-5-E34F26?style=for-the-badge&logo=html5&logoColor=white)&nbsp;
![CSS3](https://img.shields.io/badge/CSS-3-1572B6?style=for-the-badge&logo=css3&logoColor=white)&nbsp;
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)&nbsp;
![Jinja2](https://img.shields.io/badge/Jinja2-Templating-B41717?style=for-the-badge&logo=jinja&logoColor=white)&nbsp;

![Academic Project](https://img.shields.io/badge/License-Academic-blueviolet?style=for-the-badge&logo=bookstack&logoColor=white)&nbsp;
![Made in Pakistan](https://img.shields.io/badge/Made%20In-Pakistan-006600?style=for-the-badge&logo=pakistan&logoColor=white)


---

## 📌 Features

- 🧑‍⚖️ **Role-Based Access Control**
  - **Admins** have full CRUD access.
  - **Users** can view data and request operations with admin confirmation.

## 🧾 Entity Management

This application allows structured management of various investigation-related entities. The access and permitted operations depend on the user role:

| Entity            | Add         | View       | Edit                                          | Delete      |
|-------------------|-------------|------------|-----------------------------------------------|-------------|
| **Police Officers** | ✅ (Admin)  | ✅ (All)   | ✅ (Admin)                                     | ✅ (Admin)   |
| **Criminals**       | ✅ (Admin)  | ✅ (All)   | ✅ (Admin)<br>_Only status editable_          | ✅ (Admin)   |
| **Crimes**          | ✅ (Admin)  | ✅ (All)   | ❌                                            | ✅ (Admin)   |
| **Cases**           | ✅ (Admin)  | ✅ (All)   | ✅ (Admin)<br>_Only status editable_          | ✅ (Admin)   |
| **Evidence**        | ✅ (Admin)  | ✅ (All)   | ❌                                              | ✅ (Admin)   |
| **Victims**         | ✅ (Admin)  | ✅ (All)   | ❌                                              | ✅ (Admin)   |
| **Witnesses**       | ✅ (Admin)  | ✅ (All)   | ❌                                              | ✅ (Admin)   |
| **Users**           | ✅ (Admin)  | ✅ (Admin) | ✅ (Admin)<br>_Only role editable_            | ✅ (Admin)   |

🧑‍💼 **Admin Access**: Full CRUD (Create, Read, Update, Delete) for all entities.  
👤 **User Access**: View-only access to all entities.

> 🔒 Edit permissions are selectively restricted: only `criminal status`, `case status`, and `user roles` are editable via the UI. Other fields remain read-only after creation.

---

- 🧠 **Smart Dashboard**
  - Stylish UI with summary cards (counts, metrics, quick navigation).
  - Dynamic links to detailed views.

- 🔍 **Relational Insights**
  - Crimes auto-display related Evidence, Victims, and Witnesses via `crime_id`.
  - Recent entries sorted using `created_at` timestamps.

- 🧮 **Database Design**
  - Normalized schema with clear foreign key relationships.
  - SQL views are not yet implemented.  
> Planned future implementation will involve SQL views to offer optimized and secure read access for non-admin users.


---

## 🧱 Database Schema

```text
📦 Criminal
📦 PoliceOfficer
📦 PoliceStation
📦 Crime
📦 Victim
📦 Witness
📦 Evidence
📦 Cases
📦 User (Login System)```
```

## 🧠 Future Improvements

- 📜 Add login attempt logs & audit trails for better security and accountability  
- 🧾 PDF report generation for printable case summaries and records  
- 🗺️ Map-based visualization using **Leaflet.js** or **Google Maps API** for geo-tagged crime data  
- 🔌 REST API support for seamless third-party integration and automation

---
> 📄 **Note:** Create your own `.env` file in the project root directory to store sensitive configuration details like database credentials, secret keys, etc.  
> Example:
> ```
> DB_USERNAME='your_mysql_user'
> DB_PASSWORD='your_mysql_password'
> DB_HOST='your_host'
> DB_NAME='your_database_name'
> ADMIN_SECURITY_KEY='your_secret_key'
> ```

## 👨‍💻 Author 

**Muhammad Maaz Wali Khan**  
📚 _DBMS University Project_  
🔗 [GitHub: @mmaazwk27](https://github.com/mmaazwk27)
### Collaborators
- **Alisha Ather**
-- 🔗 [GitHub: @alishaather](https://github.com/alishaather)
- **Mehak Duseja**
-- 🔗 [GitHub: @MehakDuseja](https://github.com/MehakDuseja)
- **Eman Zaheer**
-- 🔗 [GitHub: @emanzaheer](https://github.com/emanzaheer)

## 🛡️ Security Disclaimer
This project is for educational purposes only. It lacks enterprise-grade encryption and authentication. Please ensure that the shared_directory does not contain sensitive personal data.

## 📄 License
This project is licensed under the Apache License 2.0. See the LICENSE file for details.
