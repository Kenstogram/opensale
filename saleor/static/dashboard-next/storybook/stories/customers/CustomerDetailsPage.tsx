import { Omit } from "@material-ui/core";
import { storiesOf } from "@storybook/react";
import * as React from "react";

import CustomerDetailsPage, {
  CustomerDetailsPageProps
} from "../../../customers/components/CustomerDetailsPage";
import { customer } from "../../../customers/fixtures";
import Decorator from "../../Decorator";
import { formError } from "../../misc";

const props: Omit<CustomerDetailsPageProps, "classes"> = {
  customer,
  disabled: false,
  errors: [],
  onAddressManageClick: () => undefined,
  onBack: () => undefined,
  onDelete: () => undefined,
  onRowClick: () => undefined,
  onSubmit: () => undefined,
  onViewAllOrdersClick: () => undefined,
  saveButtonBar: "default"
};

storiesOf("Views / Customers / Customer details", module)
  .addDecorator(Decorator)
  .add("default", () => <CustomerDetailsPage {...props} />)
  .add("loading", () => (
    <CustomerDetailsPage {...props} customer={undefined} disabled={true} />
  ))
  .add("form errors", () => (
    <CustomerDetailsPage
      {...props}
      errors={[formError("email"), formError("note")]}
    />
  ))
  .add("different addresses", () => (
    <CustomerDetailsPage
      {...props}
      customer={{
        ...customer,
        defaultBillingAddress: {
          ...customer.defaultBillingAddress,
          id: "AvSduf72="
        }
      }}
    />
  ))
  .add("never logged", () => (
    <CustomerDetailsPage
      {...props}
      customer={{
        ...customer,
        lastLogin: null
      }}
    />
  ))
  .add("never placed order", () => (
    <CustomerDetailsPage
      {...props}
      customer={{
        ...customer,
        lastPlacedOrder: {
          ...customer.lastPlacedOrder,
          edges: []
        }
      }}
    />
  ));
