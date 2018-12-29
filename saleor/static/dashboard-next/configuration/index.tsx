import * as React from "react";
import Navigator from "../components/Navigator";

import { UserContext } from "../auth";
import { WindowTitle } from "../components/WindowTitle";
import i18n from "../i18n";
import AccountCircle from "../icons/AccountCircle";
import Folder from "../icons/Folder";
import LocalShipping from "../icons/LocalShipping";
import Monetization from "../icons/Monetization";
import Navigation from "../icons/Navigation";
import Pages from "../icons/Pages";
import StoreMall from "../icons/StoreMall";
import { productTypeListUrl } from "../productTypes/urls";
import { siteSettingsUrl } from "../siteSettings/urls";
import { staffListUrl } from "../staff/urls";
import { PermissionEnum } from "../types/globalTypes";
import ConfigurationPage, { MenuItem } from "./ConfigurationPage";

export const configurationMenu: MenuItem[] = [
  {
    description: i18n.t("Define types of products you sell"),
    icon: <Folder fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_PRODUCTS,
    title: i18n.t("Product Types"),
    url: productTypeListUrl
  },
  {
    description: i18n.t("Manage your employees and their permissions"),
    icon: <AccountCircle fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_STAFF,
    title: i18n.t("Staff Members"),
    url: staffListUrl
  },
  {
    description: i18n.t("Manage how you ship out orders."),
    icon: <LocalShipping fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_SHIPPING,
    title: i18n.t("Shipping Methods")
  },
  {
    description: i18n.t("Manage how your store charges tax"),
    icon: <Monetization fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_PRODUCTS,
    title: i18n.t("Taxes")
  },
  {
    description: i18n.t("Define how users can navigate through your store"),
    icon: <Navigation fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_MENUS,
    title: i18n.t("Navigation")
  },
  {
    description: i18n.t("View and update your site settings"),
    icon: <StoreMall fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_SETTINGS,
    title: i18n.t("Site Settings"),
    url: siteSettingsUrl
  },
  {
    description: i18n.t("Manage and add additional pages"),
    icon: <Pages fontSize="inherit" />,
    permission: PermissionEnum.MANAGE_PAGES,
    title: i18n.t("Pages")
  }
];

export const configurationMenuUrl = "/configuration/";

export const ConfigurationSection: React.StatelessComponent = () => (
  <UserContext.Consumer>
    {({ user }) => (
      <Navigator>
        {navigate => (
          <>
            <WindowTitle title={i18n.t("Configuration")} />
            <ConfigurationPage
              menu={configurationMenu}
              user={user}
              onSectionClick={navigate}
            />
          </>
        )}
      </Navigator>
    )}
  </UserContext.Consumer>
);
export default ConfigurationSection;
