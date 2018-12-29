import * as React from "react";

import { CardSpacer } from "../../../components/CardSpacer";
import Container from "../../../components/Container";
import Form from "../../../components/Form";
import PageHeader from "../../../components/PageHeader";
import SeoForm from "../../../components/SeoForm";
import i18n from "../../../i18n";
import { UserError } from "../../../types";
import CategoryDetailsForm from "../../components/CategoryDetailsForm";

import { ConfirmButtonTransitionState } from "../../../components/ConfirmButton/ConfirmButton";
import SaveButtonBar from "../../../components/SaveButtonBar/SaveButtonBar";

interface FormData {
  description: string;
  name: string;
  seoTitle: string;
  seoDescription: string;
}

const initialData: FormData = {
  description: "",
  name: "",
  seoDescription: "",
  seoTitle: ""
};

export interface CategoryCreatePageProps {
  errors: UserError[];
  disabled: boolean;
  saveButtonBarState: ConfirmButtonTransitionState;
  onSubmit(data: FormData);
  onBack();
}

export const CategoryCreatePage: React.StatelessComponent<
  CategoryCreatePageProps
> = ({
  disabled,
  onSubmit,
  onBack,
  errors: userErrors,
  saveButtonBarState
}) => (
  <Form
    onSubmit={onSubmit}
    initial={initialData}
    errors={userErrors}
    confirmLeave
  >
    {({ data, change, errors, submit, hasChanged }) => (
      <Container width="md">
        <PageHeader title={i18n.t("Add Category")} onBack={onBack} />
        <div>
          <CategoryDetailsForm
            disabled={disabled}
            data={data}
            onChange={change}
            errors={errors}
          />
          <CardSpacer />
          <SeoForm
            helperText={i18n.t(
              "Add search engine title and description to make this product easier to find"
            )}
            title={data.seoTitle}
            titlePlaceholder={data.name}
            description={data.seoDescription}
            descriptionPlaceholder={data.description}
            loading={disabled}
            onChange={change}
            disabled={disabled}
          />
          <SaveButtonBar
            onCancel={onBack}
            onSave={submit}
            labels={{
              save: i18n.t("Save category")
            }}
            state={saveButtonBarState}
            disabled={disabled || !hasChanged}
          />
        </div>
      </Container>
    )}
  </Form>
);
CategoryCreatePage.displayName = "CategoryCreatePage";
export default CategoryCreatePage;
