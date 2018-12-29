/* tslint:disable */
// This file was automatically generated and should not be edited.

import { StaffInput, PermissionEnum } from "./../../types/globalTypes";

// ====================================================
// GraphQL mutation operation: StaffMemberUpdate
// ====================================================

export interface StaffMemberUpdate_staffUpdate_errors {
  __typename: "Error";
  field: string | null;
  message: string | null;
}

export interface StaffMemberUpdate_staffUpdate_user_permissions {
  __typename: "PermissionDisplay";
  code: PermissionEnum;
  name: string;
}

export interface StaffMemberUpdate_staffUpdate_user {
  __typename: "User";
  id: string;
  email: string;
  isActive: boolean;
  permissions: (StaffMemberUpdate_staffUpdate_user_permissions | null)[] | null;
}

export interface StaffMemberUpdate_staffUpdate {
  __typename: "StaffUpdate";
  errors: (StaffMemberUpdate_staffUpdate_errors | null)[] | null;
  user: StaffMemberUpdate_staffUpdate_user | null;
}

export interface StaffMemberUpdate {
  staffUpdate: StaffMemberUpdate_staffUpdate | null;
}

export interface StaffMemberUpdateVariables {
  id: string;
  input: StaffInput;
}
