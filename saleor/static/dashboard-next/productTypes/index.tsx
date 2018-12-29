import { parse as parseQs } from "qs";
import * as React from "react";
import { Route, RouteComponentProps, Switch } from "react-router-dom";

import { WindowTitle } from "../components/WindowTitle";
import i18n from "../i18n";
import {
  productTypeAddPath,
  productTypeListPath,
  productTypePath
} from "./urls";
import ProductTypeCreate from "./views/ProductTypeCreate";
import ProductTypeListComponent, {
  ProductTypeListQueryParams
} from "./views/ProductTypeList";
import ProductTypeUpdateComponent from "./views/ProductTypeUpdate";

const ProductTypeList: React.StatelessComponent<RouteComponentProps<{}>> = ({
  location
}) => {
  const qs = parseQs(location.search.substr(1));
  const params: ProductTypeListQueryParams = {
    after: qs.after,
    before: qs.before
  };
  return <ProductTypeListComponent params={params} />;
};

interface ProductTypeUpdateRouteParams {
  id: string;
}
const ProductTypeUpdate: React.StatelessComponent<
  RouteComponentProps<ProductTypeUpdateRouteParams>
> = ({ match }) => (
  <ProductTypeUpdateComponent id={decodeURIComponent(match.params.id)} />
);

export const ProductTypeRouter: React.StatelessComponent<
  RouteComponentProps<any>
> = () => (
  <>
    <WindowTitle title={i18n.t("Product types")} />
    <Switch>
      <Route exact path={productTypeListPath} component={ProductTypeList} />
      <Route exact path={productTypeAddPath} component={ProductTypeCreate} />
      <Route path={productTypePath(":id")} component={ProductTypeUpdate} />
    </Switch>
  </>
);
ProductTypeRouter.displayName = "ProductTypeRouter";
export default ProductTypeRouter;
