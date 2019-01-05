/* tslint:disable */
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL fragment: CollectionDetailsFragment
// ====================================================

export interface CollectionDetailsFragment_backgroundImage {
  __typename: "Image";
  alt: string | null;
  url: string;
}

export interface CollectionDetailsFragment {
  __typename: "Collection";
  id: string;
  isPublished: boolean;
  name: string;
  backgroundImage: CollectionDetailsFragment_backgroundImage | null;
  description: string;
  seoDescription: string | null;
  seoTitle: string | null;
}
