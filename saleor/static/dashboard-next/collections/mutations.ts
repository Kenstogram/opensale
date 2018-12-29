import gql from "graphql-tag";

import { TypedMutation } from "../mutations";
import { collectionDetailsFragment } from "./queries";
import {
  AssignHomepageCollection,
  AssignHomepageCollectionVariables
} from "./types/AssignHomepageCollection";
import {
  CollectionAssignProduct,
  CollectionAssignProductVariables
} from "./types/CollectionAssignProduct";
import {
  CollectionUpdate,
  CollectionUpdateVariables
} from "./types/CollectionUpdate";
import {
  CreateCollection,
  CreateCollectionVariables
} from "./types/CreateCollection";
import {
  RemoveCollection,
  RemoveCollectionVariables
} from "./types/RemoveCollection";
import {
  UnassignCollectionProduct,
  UnassignCollectionProductVariables
} from "./types/UnassignCollectionProduct";

const collectionUpdate = gql`
  ${collectionDetailsFragment}
  mutation CollectionUpdate($id: ID!, $input: CollectionInput!) {
    collectionUpdate(id: $id, input: $input) {
      errors {
        field
        message
      }
      collection {
        ...CollectionDetailsFragment
      }
    }
  }
`;
export const TypedCollectionUpdateMutation = TypedMutation<
  CollectionUpdate,
  CollectionUpdateVariables
>(collectionUpdate);

const assignHomepageCollection = gql`
  mutation AssignHomepageCollection($id: ID) {
    homepageCollectionUpdate(collection: $id) {
      errors {
        field
        message
      }
      shop {
        homepageCollection {
          id
        }
      }
    }
  }
`;
export const TypedAssignHomepageCollectionMutation = TypedMutation<
  AssignHomepageCollection,
  AssignHomepageCollectionVariables
>(assignHomepageCollection);

const assignCollectionProduct = gql`
  mutation CollectionAssignProduct(
    $collectionId: ID!
    $productId: ID!
    $first: Int!
  ) {
    collectionAddProducts(collectionId: $collectionId, products: [$productId]) {
      errors {
        field
        message
      }
      collection {
        id
        products(first: $first) {
          edges {
            node {
              id
              isPublished
              name
              productType {
                id
                name
              }
              thumbnailUrl
            }
          }
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
        }
      }
    }
  }
`;
export const TypedCollectionAssignProductMutation = TypedMutation<
  CollectionAssignProduct,
  CollectionAssignProductVariables
>(assignCollectionProduct);

const createCollection = gql`
  ${collectionDetailsFragment}
  mutation CreateCollection($input: CollectionCreateInput!) {
    collectionCreate(input: $input) {
      errors {
        field
        message
      }
      collection {
        ...CollectionDetailsFragment
      }
    }
  }
`;
export const TypedCollectionCreateMutation = TypedMutation<
  CreateCollection,
  CreateCollectionVariables
>(createCollection);

const removeCollection = gql`
  mutation RemoveCollection($id: ID!) {
    collectionDelete(id: $id) {
      errors {
        field
        message
      }
    }
  }
`;
export const TypedCollectionRemoveMutation = TypedMutation<
  RemoveCollection,
  RemoveCollectionVariables
>(removeCollection);

const unassignCollectionProduct = gql`
  mutation UnassignCollectionProduct(
    $collectionId: ID!
    $productId: ID!
    $first: Int
    $after: String
    $last: Int
    $before: String
  ) {
    collectionRemoveProducts(
      collectionId: $collectionId
      products: [$productId]
    ) {
      errors {
        field
        message
      }
      collection {
        id
        products(first: $first, after: $after, before: $before, last: $last) {
          edges {
            node {
              id
              isPublished
              name
              productType {
                id
                name
              }
              thumbnailUrl
            }
          }
          pageInfo {
            endCursor
            hasNextPage
            hasPreviousPage
            startCursor
          }
        }
      }
    }
  }
`;
export const TypedUnassignCollectionProductMutation = TypedMutation<
  UnassignCollectionProduct,
  UnassignCollectionProductVariables
>(unassignCollectionProduct);
