import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import * as React from "react";

import CardTitle from "../../../components/CardTitle";
import { ConfirmButtonTransitionState } from "../../../components/ConfirmButton/ConfirmButton";
import Container from "../../../components/Container";
import Form from "../../../components/Form";
import PageHeader from "../../../components/PageHeader";
import SaveButtonBar from "../../../components/SaveButtonBar";
import Skeleton from "../../../components/Skeleton";
import i18n from "../../../i18n";
import ProductImageNavigation from "../ProductImageNavigation";

const styles = (theme: Theme) =>
  createStyles({
    image: {
      height: "100%",
      objectFit: "contain",
      width: "100%"
    },
    imageContainer: {
      background: "#ffffff",
      border: "1px solid #eaeaea",
      borderRadius: theme.spacing.unit,
      margin: `0 auto ${theme.spacing.unit * 2}px`,
      maxWidth: 552,
      padding: theme.spacing.unit * 2
    },
    root: {
      display: "grid",
      gridColumnGap: theme.spacing.unit * 2 + "px",
      gridTemplateColumns: "4fr 9fr"
    }
  });

interface ProductImagePageProps extends WithStyles<typeof styles> {
  image?: {
    id: string;
    alt: string;
    url: string;
  };
  images?: Array<{
    id: string;
    url: string;
  }>;
  disabled: boolean;
  saveButtonBarState: ConfirmButtonTransitionState;
  onBack: () => void;
  onDelete: () => void;
  onRowClick: (id: string) => () => void;
  onSubmit: (data: { description: string }) => void;
}

const ProductImagePage = withStyles(styles, { name: "ProductImagePage" })(
  ({
    classes,
    disabled,
    image,
    images,
    saveButtonBarState,
    onBack,
    onDelete,
    onRowClick,
    onSubmit
  }: ProductImagePageProps) => (
    <Form
      initial={{ description: image ? image.alt : "" }}
      onSubmit={onSubmit}
      confirmLeave
    >
      {({ change, data, hasChanged, submit }) => {
        return (
          <Container width="md">
            <PageHeader title={i18n.t("Edit Photo")} onBack={onBack} />
            <div className={classes.root}>
              <div>
                <ProductImageNavigation
                  disabled={disabled}
                  images={images}
                  highlighted={image ? image.id : undefined}
                  onRowClick={onRowClick}
                />
                <Card>
                  <CardTitle title={i18n.t("Photo Information")} />
                  <CardContent>
                    <TextField
                      name="description"
                      label={i18n.t("Description")}
                      helperText={i18n.t("Optional")}
                      disabled={disabled}
                      onChange={change}
                      value={data.description}
                      multiline
                      fullWidth
                    />
                  </CardContent>
                </Card>
              </div>
              <div>
                <Card>
                  <CardTitle title={i18n.t("Photo View")} />
                  <CardContent>
                    {!!image ? (
                      <div className={classes.imageContainer}>
                        <img src={image.url} className={classes.image} />
                      </div>
                    ) : (
                      <Skeleton />
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
            <SaveButtonBar
              disabled={disabled || !onSubmit || !hasChanged}
              state={saveButtonBarState}
              onCancel={onBack}
              onDelete={onDelete}
              onSave={submit}
            />
          </Container>
        );
      }}
    </Form>
  )
);
ProductImagePage.displayName = "ProductImagePage";
export default ProductImagePage;
