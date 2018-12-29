import Card from "@material-ui/core/Card";
import { createStyles, withStyles, WithStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableFooter from "@material-ui/core/TableFooter";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Typography from "@material-ui/core/Typography";
import * as React from "react";

import Skeleton from "../../../components/Skeleton";
import TablePagination from "../../../components/TablePagination";
import i18n from "../../../i18n";
import { maybe, renderCollection, translatedTaxRates } from "../../../misc";
import { ListProps } from "../../../types";
import { ProductTypeList_productTypes_edges_node } from "../../types/ProductTypeList";

const styles = createStyles({
  leftText: {
    textAlign: "left"
  },
  link: {
    cursor: "pointer"
  },
  wideCell: {
    width: "60%"
  }
});

interface ProductTypeListProps extends ListProps, WithStyles<typeof styles> {
  productTypes: ProductTypeList_productTypes_edges_node[];
}

const ProductTypeList = withStyles(styles, { name: "ProductTypeList" })(
  ({
    classes,
    disabled,
    productTypes,
    pageInfo,
    onNextPage,
    onPreviousPage,
    onRowClick
  }: ProductTypeListProps) => (
    <Card>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell className={classes.wideCell}>
              {i18n.t("Type Name", { context: "table header" })}
            </TableCell>
            <TableCell className={classes.leftText}>
              {i18n.t("Type", { context: "table header" })}
            </TableCell>
            <TableCell className={classes.leftText}>
              {i18n.t("Tax", { context: "table header" })}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableFooter>
          <TableRow>
            <TablePagination
              colSpan={3}
              hasNextPage={pageInfo && !disabled ? pageInfo.hasNextPage : false}
              onNextPage={onNextPage}
              hasPreviousPage={
                pageInfo && !disabled ? pageInfo.hasPreviousPage : false
              }
              onPreviousPage={onPreviousPage}
            />
          </TableRow>
        </TableFooter>
        <TableBody>
          {renderCollection(
            productTypes,
            productType => (
              <TableRow
                className={!!productType ? classes.link : undefined}
                hover={!!productType}
                key={productType ? productType.id : "skeleton"}
              >
                <TableCell
                  onClick={productType ? onRowClick(productType.id) : undefined}
                >
                  {productType ? (
                    <>
                      {productType.name}
                      <Typography variant="caption">
                        {maybe(() => productType.hasVariants)
                          ? i18n.t("Configurable", { context: "product type" })
                          : i18n.t("Simple product", {
                              context: "product type"
                            })}
                      </Typography>
                    </>
                  ) : (
                    <Skeleton />
                  )}
                </TableCell>
                <TableCell className={classes.leftText}>
                  {maybe(() => productType.isShippingRequired) !== undefined ? (
                    productType.isShippingRequired ? (
                      <>{i18n.t("Physical", { context: "product type" })}</>
                    ) : (
                      <>{i18n.t("Digital", { context: "product type" })}</>
                    )
                  ) : (
                    <Skeleton />
                  )}
                </TableCell>
                <TableCell className={classes.leftText}>
                  {maybe(() => productType.taxRate) ? (
                    translatedTaxRates()[productType.taxRate]
                  ) : (
                    <Skeleton />
                  )}
                </TableCell>
              </TableRow>
            ),
            () => (
              <TableRow>
                <TableCell colSpan={3}>
                  {i18n.t("No product types found")}
                </TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
    </Card>
  )
);
ProductTypeList.displayName = "ProductTypeList";
export default ProductTypeList;
