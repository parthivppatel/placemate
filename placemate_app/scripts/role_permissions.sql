INSERT INTO "Permissions" (id,name, description) VALUES (1,'view_dashboard', 'Permission to view dashboards');

INSERT INTO "Permissions" (id,name, description) VALUES (2,'register_company', 'Permission to register the new companies');

INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(1,1,1);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(2,2,1);
INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(3,3,1);

INSERT INTO "Role_Permission" (id,role_id, permission_id) VALUES(4,3,2);

