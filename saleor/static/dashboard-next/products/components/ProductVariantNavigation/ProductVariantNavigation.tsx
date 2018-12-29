import Card from "@material-ui/core/Card";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableRow from "@material-ui/core/TableRow";
import * as classNames from "classnames";
import * as React from "react";

import CardTitle from "../../../components/CardTitle";
import Skeleton from "../../../components/Skeleton";
import TableCellAvatar from "../../../components/TableCellAvatar";
import i18n from "../../../i18n";
import { maybe, renderCollection } from "../../../misc";
import { ProductVariantCreateData_product_variants } from "../../types/ProductVariantCreateData";
import { ProductVariantDetails_productVariant } from "../../types/ProductVariantDetails";

const styles = (theme: Theme) =>
  createStyles({
    link: {
      cursor: "pointer"
    },
    tabActive: {
      "&:before": {
        background: theme.palette.primary.main,
        content: '""',
        height: "100%",
        left: 0,
        position: "absolute",
        top: 0,
        width: 2
      },
      position: "relative"
    },
    textLeft: {
      textAlign: [["left"], "!important"] as any
    }
  });

interface ProductVariantNavigationProps extends WithStyles<typeof styles> {
  current?: string;
  variants:
    | ProductVariantDetails_productVariant[]
    | ProductVariantCreateData_product_variants[];
  onRowClick: (variantId: string) => void;
}

const ProductVariantNavigation = withStyles(styles, {
  name: "ProductVariantNavigation"
})(
  ({
    classes,
    current,
    variants,
    onRowClick
  }: ProductVariantNavigationProps) => (
    <Card>
      <CardTitle title={i18n.t("Variants")} />
      <Table>
        <TableBody>
          {renderCollection(
            variants,
            variant => (
              <TableRow
                hover={!!variant}
                key={variant ? variant.id : "skeleton"}
                className={classes.link}
                onClick={variant ? () => onRowClick(variant.id) : undefined}
              >
                <TableCellAvatar
                  className={classNames({
                    [classes.tabActive]: variant && variant.id === current
                  })}
                  thumbnail={maybe(() => variant.images[0].url)}
                />
                <TableCell className={classes.textLeft}>
                  {variant ? variant.name || variant.sku : <Skeleton />}
                </TableCell>
              </TableRow>
            ),
            () => (
              <TableRow>
                <TableCell>{i18n.t("This product has no variants")}</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
    </Card>
  )
);
ProductVariantNavigation.displayName = "ProductVariantNavigation";
export default ProductVariantNavigation;
