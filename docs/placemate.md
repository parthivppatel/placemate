
# Placemate – Concept Breakdown

This document lists the key concepts integral to the **Placemate** project, categorized into:

- **Object** – a key entity or component.
- **Context** – the environment or scenario in which the object is used.
- **Information** – relevant data or rules applicable to the object in the given context.

---

## 1. User

- **Context**: Authentication, Role-based Access
- **Information**:
  - `user_id`, `email`, `password_hash`
  - Linked roles (Student, SPC)

---

## 2. Role

- **Context**: Access control
- **Information**:
  - Role types: Student, SPC
  - Assigned via `user_roles` mapping table
  - Determines dashboard and permissions

---

## 3. Permission

- **Context**: Authorization
- **Information**:
  - CRUD permissions per feature (view_company, edit_job, etc.)
  - Mapped via `role_permission_mapper`

---

## 4. Company

- **Context**: Drives, Job Posting
- **Information**:
  - `company_id`, `company_name`, `industry`, `size`
  - Contact info, active status
  - Can post multiple jobs, manage drives

---

## 5. Student

- **Context**: Job Application, Eligibility Checking
- **Information**:
  - Academic records (CGPA, 10th, 12th, diploma, UG)
  - Branch, resume link
  - Application status for drives

---

## 6. Job

- **Context**: Posted under Drives
- **Information**:
  - `job_title`, `description`, `job_type`, `mode`
  - Package: `salary_package_min` / `max`
  - Eligibility filters (min CGPA, backlogs, branches)

---

## 7. Company Drive

- **Context**: Central event managed by SPC
- **Information**:
  - `drive_id`, `company_id`, `drive_date`, `venue`
  - Related jobs under the same drive
  - Students shortlisted for participation

---

## 8. Application

- **Context**: Student applies for Job in a Drive
- **Information**:
  - `application_id`, `student_id`, `job_id`, `status`
  - Statuses: Applied, Shortlisted, Rejected, Selected

---
  
## 9. Branch & Course

- **Context**: Filters for Job/Student eligibility
- **Information**:
  - Each course is mapped to a branch
  - Used in eligibility & dashboard filtering

---
  