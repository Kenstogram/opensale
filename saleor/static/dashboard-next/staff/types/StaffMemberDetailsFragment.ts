/* tslint:disable */
// This file was automatically generated and should not be edited.

import { PermissionEnum } from "./../../types/globalTypes";

// ====================================================
// GraphQL fragment: StaffMemberDetailsFragment
// ====================================================

export interface StaffMemberDetailsFragment_permissions {
  __typename: "PermissionDisplay";
  code: PermissionEnum;
  name: string;
}

export interface StaffMemberDetailsFragment {
  __typename: "User";
  id: string;
  email: string;
  isActive: boolean;
  permissions: (StaffMemberDetailsFragment_permissions | null)[] | null;
}
