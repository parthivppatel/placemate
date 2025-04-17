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

INSERT INTO "Permissions" (id,name, description) VALUES (20,'edit_students','Permission to edit student details');
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(38,1,20);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(39,3,20);

INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(40, 1, 12);
