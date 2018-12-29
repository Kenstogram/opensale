import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import { createStyles, withStyles, WithStyles } from "@material-ui/core/styles";
import * as React from "react";

import ConfirmButton, {
  ConfirmButtonTransitionState
} from "../../../components/ConfirmButton";
import Form from "../../../components/Form";
import { SingleAutocompleteSelectField } from "../../../components/SingleAutocompleteSelectField";
import i18n from "../../../i18n";

export interface FormData {
  quantity: number;
  variant: {
    label: string;
    value: string;
  };
}

const styles = createStyles({
  overflow: {
    overflowY: "visible"
  }
});

interface OrderProductAddDialogProps extends WithStyles<typeof styles> {
  confirmButtonState: ConfirmButtonTransitionState;
  open: boolean;
  variants?: Array<{
    id: string;
    name: string;
    sku: string;
    stockQuantity: number;
  }>;
  loading: boolean;
  fetchVariants: (value: string) => void;
  onClose: () => void;
  onSubmit: (data: FormData) => void;
}

const initialForm: FormData = {
  quantity: 1,
  variant: {
    label: "",
    value: ""
  }
};

const OrderProductAddDialog = withStyles(styles, {
  name: "OrderProductAddDialog"
})(
  ({
    classes,
    confirmButtonState,
    open,
    loading,
    variants,
    fetchVariants,
    onClose,
    onSubmit
  }: OrderProductAddDialogProps) => (
    <Dialog
      open={open}
      classes={{ paper: classes.overflow }}
      fullWidth
      maxWidth="sm"
    >
      <Form initial={initialForm} onSubmit={onSubmit}>
        {({ data, change }) => {
          const choices =
            !loading && variants
              ? variants.map(v => ({
                  label: `${v.sku} ${v.name}`,
                  value: v.id
                }))
              : [];
          return (
            <>
              <DialogTitle>{i18n.t("Add product")}</DialogTitle>
              <DialogContent className={classes.overflow}>
                <SingleAutocompleteSelectField
                  name="variant"
                  value={data.variant}
                  choices={choices}
                  onChange={change}
                  fetchChoices={fetchVariants}
                  loading={loading}
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={onClose}>
                  {i18n.t("Cancel", { context: "button" })}
                </Button>
                <ConfirmButton
                  transitionState={confirmButtonState}
                  color="primary"
                  variant="contained"
                  type="submit"
                >
                  {i18n.t("Confirm", { context: "button" })}
                </ConfirmButton>
              </DialogActions>
            </>
          );
        }}
      </Form>
    </Dialog>
  )
);
OrderProductAddDialog.displayName = "OrderProductAddDialog";
export default OrderProductAddDialog;
