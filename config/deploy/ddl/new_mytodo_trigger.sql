--------------------------------------------------------
--  已建立檔案 - 星期四-二月-01-2018   
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Trigger ACTIVITY_CATEGORY_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."ACTIVITY_CATEGORY_TR" 
BEFORE INSERT ON ACTIVITY_CATEGORY
FOR EACH ROW
 WHEN (new."ACTIVITY_CAT_ID" IS NULL) BEGIN
    SELECT "SEQ_ACTIVITY_CAT_ID".nextval
        INTO :new."ACTIVITY_CAT_ID" FROM dual;   
END;
/
ALTER TRIGGER "MYTODO"."ACTIVITY_CATEGORY_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger ACTIVITY_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."ACTIVITY_TR" 
BEFORE INSERT ON ACTIVITY
FOR EACH ROW
 WHEN (new."ACTIVITY_ID" IS NULL) BEGIN
    SELECT "SEQ_ACTIVITY_ID".nextval
        INTO :new."ACTIVITY_ID" FROM dual;   
END;
/
ALTER TRIGGER "MYTODO"."ACTIVITY_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_GROUP_PERMISSIONS_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_GROUP_PERMISSIONS_TR" 
BEFORE INSERT ON "AUTH_GROUP_PERMISSIONS"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_GROUP_PERMISSIONS_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_GROUP_PERMISSIONS_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_GROUP_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_GROUP_TR" 
BEFORE INSERT ON "AUTH_GROUP"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_GROUP_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_GROUP_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_PERMISSION_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_PERMISSION_TR" 
BEFORE INSERT ON "AUTH_PERMISSION"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_PERMISSION_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_PERMISSION_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_USER_GROUPS_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_USER_GROUPS_TR" 
BEFORE INSERT ON "AUTH_USER_GROUPS"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_USER_GROUPS_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_USER_GROUPS_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_USER_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_USER_TR" 
BEFORE INSERT ON "AUTH_USER"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_USER_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_USER_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger AUTH_USER_USER_PERMISSIONS_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."AUTH_USER_USER_PERMISSIONS_TR" 
BEFORE INSERT ON "AUTH_USER_USER_PERMISSIONS"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "AUTH_USER_USER_PERMISSIONS_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."AUTH_USER_USER_PERMISSIONS_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger CR_REVIEWCOMMENTS_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."CR_REVIEWCOMMENTS_TR" 
BEFORE INSERT ON CR_REVIEWCOMMENTS
FOR EACH ROW
 WHEN (new."ID" IS NULL) BEGIN
    SELECT "SEQ_CR_REVIEWCOMMENTS_ID".nextval
        INTO :new."ID" FROM dual;   
END;
/
ALTER TRIGGER "MYTODO"."CR_REVIEWCOMMENTS_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger DJANGO_ADMIN_LOG_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."DJANGO_ADMIN_LOG_TR" 
BEFORE INSERT ON "DJANGO_ADMIN_LOG"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "DJANGO_ADMIN_LOG_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."DJANGO_ADMIN_LOG_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger DJANGO_CONTENT_TYPE_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."DJANGO_CONTENT_TYPE_TR" 
BEFORE INSERT ON "DJANGO_CONTENT_TYPE"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "DJANGO_CONTENT_TYPE_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."DJANGO_CONTENT_TYPE_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger DJANGO_MIGRATIONS_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."DJANGO_MIGRATIONS_TR" 
BEFORE INSERT ON "DJANGO_MIGRATIONS"
FOR EACH ROW
  WHEN (new."ID" IS NULL) BEGIN
        SELECT "DJANGO_MIGRATIONS_SQ".nextval
        INTO :new."ID" FROM dual;
    END;


/
ALTER TRIGGER "MYTODO"."DJANGO_MIGRATIONS_TR" ENABLE;
