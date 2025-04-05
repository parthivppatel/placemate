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

