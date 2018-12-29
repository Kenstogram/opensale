import { empty, only } from "../misc";
import { OrderStatusFilter } from "../types/globalTypes";
import { OrderListFilterTabs } from "./components/OrderListFilter";
import { OrderListQueryParams } from "./views/OrderList";

export const getTabName = (qs: OrderListQueryParams): OrderListFilterTabs => {
  const filters = {
    status: qs.status
  };
  if (empty(filters)) {
    return "all";
  }
  if (only(filters, "status")) {
    switch (filters.status) {
      case OrderStatusFilter.READY_TO_CAPTURE:
        return "toCapture";
      case OrderStatusFilter.READY_TO_FULFILL:
        return "toFulfill";
    }
  }
  return "custom";
};
