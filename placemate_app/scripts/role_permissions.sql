INSERT INTO "Permissions" (id,name, description) VALUES (1,'view_dashboard', 'Permission to view dashboards');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(1,1,1);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(2,2,1);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(3,3,1);

INSERT INTO "Permissions" (id,name, description) VALUES (2,'register_company', 'Permission to register the new companies');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(4,3,2);

INSERT INTO "Permissions" (id,name, description) VALUES (3,'view_company', 'Permission to view the company');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(5,1,3);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(6,2,3);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(7,3,3);

INSERT INTO "Permissions" (id,name, description) VALUES (4,'view_companies', 'Permission to view the companies list');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(8,1,4);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(9,3,4);

INSERT INTO "Permissions" (id,name, description) VALUES (5,'edit_company', 'Permission to edit the company details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(10,3,5);

INSERT INTO "Permissions" (id,name, description) VALUES (6,'delete_company', 'Permission to delete the company details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(11,3,6);

INSERT INTO "Permissions" (id,name, description) VALUES (7,'post_job', 'Permission to post the new jobs');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(12,2,7);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(13,3,7);

INSERT INTO "Permissions" (id,name, description) VALUES (8,'edit_job', 'Permission to edit the job details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(14,2,8);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(15,3,8);

INSERT INTO "Permissions" (id,name, description) VALUES (9,'view_jobs','Permission to view the job list');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(16,1,9);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(17,3,9);

INSERT INTO "Permissions" (id,name, description) VALUES (10,'view_job','Permission to view the specific job details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(18,1,10);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(19,2,10);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(20,3,10);

INSERT INTO "Permissions" (id,name, description) VALUES (11,'delete_job','Permission to delete the job details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(21,2,11);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(22,3,11);

INSERT INTO "Permissions" (id, name, description)  VALUES (12, 'view_students', 'Permission to view students details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(23,2,12);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(24,3,12);

INSERT INTO "Permissions" (id, name, description) VALUES (13, 'delete_students', 'Permission to delete students');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(25,2,13);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(26,3,13);

INSERT INTO "Permissions" (id, name, description) VALUES (14, 'add_students', 'Permission to add/create students');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES (28, 3, 14);

INSERT INTO "Permissions" (id,name, description) VALUES (15,'add_drive', 'Permission to add the new drive');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(29,2,15);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(30,3,15);

INSERT INTO "Permissions" (id,name, description) VALUES (16,'edit_drive', 'Permission to edit the drive details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(31,3,16);

INSERT INTO "Permissions" (id,name, description) VALUES (17,'view_drives','Permission to view the drives list');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(32,1,17);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(33,3,17);

INSERT INTO "Permissions" (id,name, description) VALUES (18,'view_drive','Permission to view the specific drive details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(34,1,18);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(35,2,18);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(36,3,18);

INSERT INTO "Permissions" (id,name, description) VALUES (19,'delete_drive','Permission to delete the drive details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(37,3,19);

INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(40, 1, 12);

INSERT INTO "Permissions" (id,name, description) VALUES (21,'view_applicants','Permission to view applicant details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(41,3,21);

INSERT INTO "Permissions" (id,name, description) VALUES (22,'application_action','Approve/Reject the application');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(42,2,22);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(43,3,22);

INSERT INTO "Permissions" (id,name, description) VALUES (23,'placement_action','Approve/Reject the placement application');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(44,2,23);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(45,3,23);

INSERT INTO "Permissions" (id, name, description) VALUES (24, 'student_view_profile', 'Students Permission to view student their details');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(46, 1, 24);

INSERT INTO "Permissions" (id, name, description) VALUES (25, 'student_edit_profile', 'Students Permission to edit their student details');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(47, 1, 25);

INSERT INTO "Permissions" (id, name, description) VALUES (26, 'student_view_drives', 'Students Permission to view list of drives');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(48, 1, 26);

INSERT INTO "Permissions" (id, name, description) VALUES (27, 'student_view_drive', 'Students Permission to view specific drive details');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(49, 1, 27);

INSERT INTO "Permissions" (id, name, description) VALUES (28, 'student_view_applications', 'Students Permission to view their applications');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(50, 1, 28);

INSERT INTO "Permissions" (id, name, description) VALUES (29, 'edit_students', 'PlacementCell Permission to view their applications');
INSERT INTO "Role_Permission" (id, role_id, permission_id) VALUES(51, 3, 29);

INSERT INTO "Permissions" (id,name, description) VALUES (30,'view_members','can view placement members list');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(52,3,30); 

INSERT INTO "Permissions" (id,name, description) VALUES (31,'view_member','can view specific placement member profile');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(53,3,31); 

INSERT INTO "Permissions" (id,name, description) VALUES (32,'add_member','can add new placement member');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(54,3,32); 

-- INSERT INTO "Permissions" (id,name, description) VALUES (33,'delete_member','can delete plaecment member');
-- INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(55,3,33); 
 
-- INSERT INTO "Permissions" (id,name, description) VALUES (34,'edit_member','can edit placement member details');
-- INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(56,3,34); 

delete from "Role_Permission" where id in(55,56); 

INSERT INTO placement_cell_members (id_id, role_in_cell, branch_id, join_date, end_date, active_status, created_at, updated_at)
VALUES (154, 'Student Coordinator', 3, '2023-08-01 00:00:00', NULL, TRUE, '2023-08-01 00:00:00', '2023-08-01 00:00:00');