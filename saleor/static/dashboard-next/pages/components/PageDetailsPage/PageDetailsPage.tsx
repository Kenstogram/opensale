import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import * as React from "react";

import { ConfirmButtonTransitionState } from "../../../components/ConfirmButton/ConfirmButton";
import { Container } from "../../../components/Container";
import Form, { FormProps } from "../../../components/Form";
import PageHeader from "../../../components/PageHeader";
import SaveButtonBar from "../../../components/SaveButtonBar";
import Toggle from "../../../components/Toggle";
import PageContent from "../PageContent";
import PageDeleteDialog from "../PageDeleteDialog";
import PageProperties from "../PageProperties";

interface PageInput {
  title: string;
  content: string;
  slug: string;
  availableOn: string;
  isVisible: boolean;
}

const defaultPage = {
  availableOn: "",
  content: "",
  isVisible: false,
  slug: "",
  title: ""
};

const PageForm: React.ComponentType<FormProps<PageInput>> = Form;

const styles = (theme: Theme) =>
  createStyles({
    root: {
      display: "grid",
      gridColumnGap: `${theme.spacing.unit * 2}px`,
      gridTemplateColumns: "3fr 1fr"
    }
  });

export interface PageDetailsPageProps extends WithStyles<typeof styles> {
  page?: PageInput & {
    created?: string;
  };
  errors?: Array<{
    field: string;
    message: string;
  }>;
  disabled?: boolean;
  title?: string;
  saveButtonBarState: ConfirmButtonTransitionState;
  onBack?();
  onDelete?();
  onSubmit(data: PageInput);
}

const PageDetailsPage = withStyles(styles, { name: "PageDetailsPage" })(
  ({
    classes,
    errors,
    disabled,
    page,
    title,
    saveButtonBarState,
    onBack,
    onDelete,
    onSubmit
  }: PageDetailsPageProps) => (
    <PageForm
      errors={errors}
      key={page ? "ready" : "loading"}
      initial={page ? page : defaultPage}
      onSubmit={onSubmit}
    >
      {({ change, data, errors, hasChanged, submit }) => (
        <Toggle>
          {(opened, { toggle: togglePageDeleteDialog }) => (
            <Container width="md">
              <>
                <PageHeader onBack={onBack} title={title} />
                <div className={classes.root}>
                  <div>
                    <PageContent
                      errors={errors}
                      loading={disabled}
                      onChange={change}
                      content={data.content}
                      title={data.title}
                    />
                  </div>
                  <div>
                    <PageProperties
                      availableOn={data.availableOn}
                      created={page ? page.created : undefined}
                      isVisible={data.isVisible}
                      loading={disabled}
                      onChange={change}
                      slug={data.slug}
                    />
                  </div>
                </div>
                <SaveButtonBar
                  disabled={disabled || !onSubmit || !hasChanged}
                  state={saveButtonBarState}
                  onCancel={onBack}
                  onDelete={togglePageDeleteDialog}
                  onSave={submit}
                />
                {!disabled && (
                  <PageDeleteDialog
                    opened={opened}
                    onConfirm={onDelete}
                    onClose={togglePageDeleteDialog}
                    title={page.title}
                  />
                )}
              </>
            </Container>
          )}
        </Toggle>
      )}
    </PageForm>
  )
);
PageDetailsPage.displayName = "PageDetailsPage";
export default PageDetailsPage;
