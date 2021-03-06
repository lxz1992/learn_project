--------------------------------------------------------
--  File created - Tuesday-March-13-2018   
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Table OAUTH2_PROVIDER_ACCESSTOKEN
--------------------------------------------------------

  CREATE TABLE "MYTODO"."OAUTH2_PROVIDER_ACCESSTOKEN" 
   (	"ID" NUMBER(19,0), 
	"TOKEN" NVARCHAR2(255), 
	"EXPIRES" DATE, 
	"SCOPE" NCLOB, 
	"CREATED" DATE, 
	"UPDATED" DATE, 
	"USER_ID" NUMBER(11,0), 
	"APPLICATION_ID" NUMBER
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" 
 LOB ("SCOPE") STORE AS (
  TABLESPACE "MYTODO" ENABLE STORAGE IN ROW CHUNK 8192 PCTVERSION 10
  NOCACHE LOGGING 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)) ;
--------------------------------------------------------
--  DDL for Table OAUTH2_PROVIDER_APPLICATION
--------------------------------------------------------

  CREATE TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" 
   (	"DESCRIPTION" NVARCHAR2(256), 
	"PRIVATE_SCOPES" NVARCHAR2(256), 
	"LOGO" NVARCHAR2(100), 
	"IS_ANONYMOUS" NUMBER(1,0) DEFAULT 0, 
	"WEBSITE" NVARCHAR2(200), 
	"PRIVACY_POLICY" NVARCHAR2(200), 
	"CREATED" DATE, 
	"UPDATED" DATE, 
	"REQUIRED_SCOPES" VARCHAR2(20 BYTE), 
	"ID" NUMBER, 
	"CLIENT_ID" NVARCHAR2(1000), 
	"REDIRECT_URIS" NCLOB, 
	"CLIENT_TYPE" NVARCHAR2(32), 
	"AUTHORIZATION_GRANT_TYPE" NVARCHAR2(32), 
	"CLIENT_SECRET" NVARCHAR2(255), 
	"NAME" NVARCHAR2(255), 
	"SKIP_AUTHORIZATION" NUMBER(1,0) DEFAULT 0, 
	"USER_ID" NUMBER(11,0)
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" 
 LOB ("REDIRECT_URIS") STORE AS (
  TABLESPACE "MYTODO" ENABLE STORAGE IN ROW CHUNK 8192 PCTVERSION 10
  NOCACHE LOGGING 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)) ;
 

   COMMENT ON COLUMN "MYTODO"."OAUTH2_PROVIDER_APPLICATION"."DESCRIPTION" IS 'Default non tracking permissions. Valid only if application is anonymous';
 
   COMMENT ON COLUMN "MYTODO"."OAUTH2_PROVIDER_APPLICATION"."PRIVATE_SCOPES" IS 'Private API scopes';
 
   COMMENT ON COLUMN "MYTODO"."OAUTH2_PROVIDER_APPLICATION"."IS_ANONYMOUS" IS 'Expression cannot use columns or user functions.  Literal strings should be quoted : false';
 
   COMMENT ON COLUMN "MYTODO"."OAUTH2_PROVIDER_APPLICATION"."PRIVACY_POLICY" IS 'Link of privacy policy of application';
 
   COMMENT ON COLUMN "MYTODO"."OAUTH2_PROVIDER_APPLICATION"."REDIRECT_URIS" IS 'Allowed URIs list, space separated';
--------------------------------------------------------
--  DDL for Table OAUTH2_PROVIDER_GRANT
--------------------------------------------------------

  CREATE TABLE "MYTODO"."OAUTH2_PROVIDER_GRANT" 
   (	"ID" NUMBER, 
	"CODE" NVARCHAR2(255), 
	"EXPIRES" DATE, 
	"REDIRECT_URI" NVARCHAR2(255), 
	"SCOPE" NCLOB, 
	"CREATED" DATE, 
	"UPDATED" DATE, 
	"APPLICATION_ID" NUMBER, 
	"USER_ID" NUMBER
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" 
 LOB ("SCOPE") STORE AS (
  TABLESPACE "MYTODO" ENABLE STORAGE IN ROW CHUNK 8192 PCTVERSION 10
  NOCACHE LOGGING 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)) ;
--------------------------------------------------------
--  DDL for Table OAUTH2_PROVIDER_REFRESHTOKEN
--------------------------------------------------------

  CREATE TABLE "MYTODO"."OAUTH2_PROVIDER_REFRESHTOKEN" 
   (	"ID" NUMBER(19,0), 
	"TOKEN" NVARCHAR2(255), 
	"CREATED" DATE, 
	"UPDATED" DATE, 
	"USER_ID" NUMBER(11,0), 
	"APPLICATION_ID" NUMBER, 
	"ACCESS_TOKEN_ID" NVARCHAR2(255)
   ) PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" ;
--------------------------------------------------------
--  DDL for Index OAUTH2_PROVIDER_ACCESSTOKE_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "MYTODO"."OAUTH2_PROVIDER_ACCESSTOKE_PK" ON "MYTODO"."OAUTH2_PROVIDER_ACCESSTOKEN" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" ;
--------------------------------------------------------
--  DDL for Index APPLICATION_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "MYTODO"."APPLICATION_PK" ON "MYTODO"."OAUTH2_PROVIDER_APPLICATION" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" ;
--------------------------------------------------------
--  DDL for Index OAUTH2_PROVIDER_GRANT_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "MYTODO"."OAUTH2_PROVIDER_GRANT_PK" ON "MYTODO"."OAUTH2_PROVIDER_GRANT" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" ;
--------------------------------------------------------
--  DDL for Index OAUTH2_PROVIDER_REFRESH_TO_PK
--------------------------------------------------------

  CREATE UNIQUE INDEX "MYTODO"."OAUTH2_PROVIDER_REFRESH_TO_PK" ON "MYTODO"."OAUTH2_PROVIDER_REFRESHTOKEN" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO" ;
--------------------------------------------------------
--  Constraints for Table OAUTH2_PROVIDER_ACCESSTOKEN
--------------------------------------------------------

  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_ACCESSTOKEN" ADD CONSTRAINT "OAUTH2_PROVIDER_ACCESSTOKE_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO"  ENABLE;
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_ACCESSTOKEN" MODIFY ("ID" NOT NULL ENABLE);
--------------------------------------------------------
--  Constraints for Table OAUTH2_PROVIDER_APPLICATION
--------------------------------------------------------

  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" ADD CONSTRAINT "APPLICATION_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO"  ENABLE;
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" MODIFY ("IS_ANONYMOUS" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" MODIFY ("CREATED" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" MODIFY ("UPDATED" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" MODIFY ("ID" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_APPLICATION" MODIFY ("USER_ID" NOT NULL ENABLE);
--------------------------------------------------------
--  Constraints for Table OAUTH2_PROVIDER_GRANT
--------------------------------------------------------

  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_GRANT" ADD CONSTRAINT "OAUTH2_PROVIDER_GRANT_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO"  ENABLE;
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_GRANT" MODIFY ("ID" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_GRANT" MODIFY ("CREATED" NOT NULL ENABLE);
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_GRANT" MODIFY ("UPDATED" NOT NULL ENABLE);
--------------------------------------------------------
--  Constraints for Table OAUTH2_PROVIDER_REFRESHTOKEN
--------------------------------------------------------

  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_REFRESHTOKEN" ADD CONSTRAINT "OAUTH2_PROVIDER_REFRESH_TO_PK" PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1 BUFFER_POOL DEFAULT)
  TABLESPACE "MYTODO"  ENABLE;
 
  ALTER TABLE "MYTODO"."OAUTH2_PROVIDER_REFRESHTOKEN" MODIFY ("ID" NOT NULL ENABLE);
--------------------------------------------------------
--  DDL for Trigger ACCESSTOKEN_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."ACCESSTOKEN_TR" 
BEFORE INSERT ON OAUTH2_PROVIDER_ACCESSTOKEN 
FOR EACH ROW 
BEGIN
  <<COLUMN_SEQUENCES>>
  BEGIN
    IF INSERTING AND :NEW.ID IS NULL THEN
      SELECT ACCESSTOKEN_SEQ.NEXTVAL INTO :NEW.ID FROM SYS.DUAL;
    END IF;
  END COLUMN_SEQUENCES;
END;
/
ALTER TRIGGER "MYTODO"."ACCESSTOKEN_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger OAUTH_APPLICATION_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."OAUTH_APPLICATION_TR" 
BEFORE INSERT ON OAUTH2_PROVIDER_APPLICATION 
FOR EACH ROW 
BEGIN
  <<COLUMN_SEQUENCES>>
  BEGIN
    IF INSERTING AND :NEW.ID IS NULL THEN
      SELECT OAUTH_APPLICATION_SEQ.NEXTVAL INTO :NEW.ID FROM SYS.DUAL;
    END IF;
  END COLUMN_SEQUENCES;
END;
/
ALTER TRIGGER "MYTODO"."OAUTH_APPLICATION_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger OAUTH_GRANT_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."OAUTH_GRANT_TR" 
BEFORE INSERT ON OAUTH2_PROVIDER_GRANT 
FOR EACH ROW 
BEGIN
  <<COLUMN_SEQUENCES>>
  BEGIN
    IF INSERTING AND :NEW.ID IS NULL THEN
      SELECT OAUTH_GRANT_SEQ.NEXTVAL INTO :NEW.ID FROM SYS.DUAL;
    END IF;
  END COLUMN_SEQUENCES;
END;
/
ALTER TRIGGER "MYTODO"."OAUTH_GRANT_TR" ENABLE;
--------------------------------------------------------
--  DDL for Trigger OAUTH_REFRESH_TOKEN_TR
--------------------------------------------------------

  CREATE OR REPLACE TRIGGER "MYTODO"."OAUTH_REFRESH_TOKEN_TR" 
BEFORE INSERT ON OAUTH2_PROVIDER_REFRESHTOKEN 
FOR EACH ROW 
BEGIN
  <<COLUMN_SEQUENCES>>
  BEGIN
    IF INSERTING AND :NEW.ID IS NULL THEN
      SELECT OAUTH_REFRESH_TOKEN_SEQ.NEXTVAL INTO :NEW.ID FROM SYS.DUAL;
    END IF;
  END COLUMN_SEQUENCES;
END;
/
ALTER TRIGGER "MYTODO"."OAUTH_REFRESH_TOKEN_TR" ENABLE;
