import AppBar from "@material-ui/core/AppBar";
import ClickAwayListener from "@material-ui/core/ClickAwayListener";
import Drawer from "@material-ui/core/Drawer";
import Grow from "@material-ui/core/Grow";
import Hidden from "@material-ui/core/Hidden";
import IconButton from "@material-ui/core/IconButton";
import LinearProgress from "@material-ui/core/LinearProgress";
import MenuItem from "@material-ui/core/MenuItem";
import Menu from "@material-ui/core/MenuList";
import Paper from "@material-ui/core/Paper";
import Popper from "@material-ui/core/Popper";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import MenuIcon from "@material-ui/icons/Menu";
import Person from "@material-ui/icons/Person";
import PersonOutline from "@material-ui/icons/PersonOutline";
import SettingsIcon from "@material-ui/icons/Settings";
import * as classNames from "classnames";
import * as React from "react";
import SVG from "react-inlinesvg";

import { appMountPoint } from ".";
import * as saleorLogo from "../images/logo.svg";
import { UserContext } from "./auth";
import { User } from "./auth/types/User";
import { categoryListUrl } from "./categories/urls";
import { collectionListUrl } from "./collections/urls";
import AppProgress from "./components/AppProgress";
import MenuToggle from "./components/MenuToggle";
import Navigator from "./components/Navigator";
import Toggle from "./components/Toggle";
import { configurationMenu, configurationMenuUrl } from "./configuration";
import { customerListUrl } from "./customers/urls";
import i18n from "./i18n";
import ArrowDropdown from "./icons/ArrowDropdown";
import Home from "./icons/Home";
import Shop from "./icons/Shop";
import Truck from "./icons/Truck";
import { removeDoubleSlashes } from "./misc";
import { orderListUrl } from "./orders/urls";
import { productListUrl } from "./products/urls";
import { PermissionEnum } from "./types/globalTypes";

const drawerWidth = 256;
const navigationBarHeight = 64;

const menuStructure: IMenuItem[] = [
  {
    ariaLabel: "home",
    icon: <Home />,
    label: i18n.t("Home", { context: "Menu label" }),
    url: "/"
  },
  {
    ariaLabel: "catalogue",
    children: [
      {
        ariaLabel: "products",
        icon: <Shop />,
        label: i18n.t("Products", { context: "Menu label" }),
        url: productListUrl()
      },
      {
        ariaLabel: "categories",
        icon: <Shop />,
        label: i18n.t("Categories", { context: "Menu label" }),
        url: categoryListUrl
      },
      {
        ariaLabel: "collections",
        icon: <Shop />,
        label: i18n.t("Collections", { context: "Menu label" }),
        url: collectionListUrl
      }
    ],
    icon: <Shop />,
    label: i18n.t("Catalogue", { context: "Menu label" }),
    permission: PermissionEnum.MANAGE_PRODUCTS
  },
  {
    ariaLabel: "orders",
    icon: <Truck />,
    label: i18n.t("Orders", { context: "Menu label" }),
    permission: PermissionEnum.MANAGE_ORDERS,
    url: orderListUrl()
  },
  {
    ariaLabel: "customers",
    icon: <PersonOutline />,
    label: i18n.t("Customers", { context: "Menu label" }),
    permission: PermissionEnum.MANAGE_USERS,
    url: customerListUrl
  }
];

const styles = (theme: Theme) =>
  createStyles({
    appBar: {
      boxShadow: "none",
      display: "grid",
      gridTemplateColumns: `${drawerWidth}px 1fr`,
      zIndex: theme.zIndex.drawer + 1
    },
    appFrame: {
      display: "flex",
      width: "100%",
      zIndex: 1
    },
    appLoader: {
      gridColumn: "span 2",
      height: 2
    },
    arrow: {
      marginLeft: theme.spacing.unit * 2,
      position: "relative",
      top: 6,
      transition: theme.transitions.duration.standard + "ms"
    },
    container: {
      textAlign: "right",
      width: "100%"
    },
    content: {
      backgroundColor: theme.palette.background.default,
      flexGrow: 1,
      marginLeft: 0,
      marginTop: 56,
      padding: theme.spacing.unit,
      [theme.breakpoints.up("sm")]: {
        marginLeft: drawerWidth,
        padding: theme.spacing.unit * 2
      }
    },
    drawerDesktop: {
      backgroundColor: "transparent",
      borderRight: "0 none",
      height: `calc(100vh - ${navigationBarHeight + theme.spacing.unit * 2}px)`,
      marginTop: navigationBarHeight + theme.spacing.unit * 2,
      position: "fixed" as "fixed",
      width: drawerWidth
    },
    drawerMobile: {
      width: drawerWidth
    },
    email: {
      cursor: "pointer",
      display: "inline-block",
      height: 48,
      lineHeight: 48 + "px",
      marginRight: theme.spacing.unit * 2
    },
    emailLabel: {
      color: theme.palette.primary.contrastText,
      display: "inline",
      fontWeight: 600 as 600
    },
    logo: {
      "& svg": {
        height: "100%"
      },
      height: 32
    },
    menuButton: {
      marginRight: theme.spacing.unit
    },
    menuList: {
      display: "flex",
      flexDirection: "column",
      height: "100%",
      marginLeft: theme.spacing.unit * 4,
      marginTop: theme.spacing.unit * 2,
      paddingBottom: theme.spacing.unit * 3
    },
    menuListItem: {
      "&:hover": {
        color: theme.palette.primary.main
      },
      alignItems: "center",
      color: "#616161",
      display: "flex",
      height: 40,
      paddingLeft: 0,
      textDecoration: "none",
      transition: theme.transitions.duration.standard + "ms"
    },
    menuListItemText: {
      "&:hover": {
        color: theme.palette.primary.main
      },
      cursor: "pointer",
      fontSize: "1rem",
      marginLeft: theme.spacing.unit * 2,
      transition: theme.transitions.duration.standard + "ms"
    },
    menuListNested: {
      marginLeft: theme.spacing.unit * 3
    },
    root: {
      flexGrow: 1
    },
    rotate: {
      transform: "rotate(180deg)"
    },
    spacer: {
      flex: 1
    },
    toolBarContent: {
      backgroundColor: "#56D799"
    },
    toolBarMenu: {
      minHeight: 56,
      paddingLeft: theme.spacing.unit
    },
    userIcon: {
      marginRight: theme.spacing.unit
    },
    userMenuItem: {
      textAlign: "right"
    }
  });

interface ResponsiveDrawerProps extends WithStyles<typeof styles> {
  children?: React.ReactNode;
  open: boolean;
  onClose?();
}

const ResponsiveDrawer = withStyles(styles, { name: "ResponsiveDrawer" })(
  ({ children, classes, onClose, open }: ResponsiveDrawerProps) => (
    <>
      <Hidden smDown>
        <Drawer
          variant="persistent"
          open
          classes={{
            paper: classes.drawerDesktop
          }}
        >
          {children}
        </Drawer>
      </Hidden>
      <Hidden mdUp>
        <Drawer
          variant="temporary"
          onClose={onClose}
          open={open}
          classes={{ paper: classes.drawerMobile }}
        >
          {children}
        </Drawer>
      </Hidden>
    </>
  )
);

interface IMenuItem {
  ariaLabel: string;
  children?: IMenuItem[];
  icon: React.ReactNode;
  label: string;
  permission?: PermissionEnum;
  url?: string;
}
interface MenuListProps extends WithStyles<typeof styles> {
  menuItems: IMenuItem[];
  user: User;
  onMenuItemClick: (url: string, event: React.MouseEvent<any>) => void;
}
const MenuList = withStyles(styles, { name: "MenuList" })(
  ({ classes, menuItems, user, onMenuItemClick }: MenuListProps) => (
    <div>
      {menuItems.map(menuItem => {
        if (
          menuItem.permission &&
          !user.permissions.map(perm => perm.code).includes(menuItem.permission)
        ) {
          return null;
        }
        if (!menuItem.url) {
          return (
            <Toggle key={menuItem.label}>
              {(openedMenu, { toggle: toggleMenu }) => (
                <>
                  <div onClick={toggleMenu} className={classes.menuListItem}>
                    {menuItem.icon}
                    <Typography
                      aria-label={menuItem.ariaLabel}
                      className={classes.menuListItemText}
                    >
                      {menuItem.label}
                    </Typography>
                  </div>
                  {openedMenu && (
                    <div className={classes.menuListNested}>
                      <MenuList
                        menuItems={menuItem.children}
                        user={user}
                        onMenuItemClick={onMenuItemClick}
                      />
                    </div>
                  )}
                </>
              )}
            </Toggle>
          );
        }
        return (
          <a
            className={classes.menuListItem}
            href={removeDoubleSlashes(appMountPoint + menuItem.url)}
            onClick={event => onMenuItemClick(menuItem.url, event)}
            key={menuItem.label}
          >
            {menuItem.icon}
            <Typography
              aria-label={menuItem.ariaLabel}
              className={classes.menuListItemText}
            >
              {menuItem.label}
            </Typography>
          </a>
        );
      })}
    </div>
  )
);

interface AppRootState {
  open: boolean;
}

export const AppRoot = withStyles(styles, { name: "AppRoot" })(
  class InnerAppRoot extends React.Component<
    WithStyles<typeof styles>,
    AppRootState
  > {
    state = { open: false };
    anchor = React.createRef<HTMLDivElement>();

    closeDrawer = () => {
      this.setState({ open: false });
    };

    render() {
      const { children, classes } = this.props;
      const { open } = this.state;
      return (
        <AppProgress>
          {({ value: isProgressVisible }) => (
            <UserContext.Consumer>
              {({ logout, user }) => (
                <Navigator>
                  {navigate => {
                    const handleMenuItemClick = (
                      url: string,
                      event: React.MouseEvent<any>
                    ) => {
                      event.preventDefault();
                      this.closeDrawer();
                      navigate(url);
                    };
                    return (
                      <div className={classes.appFrame}>
                        <AppBar className={classes.appBar}>
                          <Toolbar
                            disableGutters
                            className={classes.toolBarMenu}
                          >
                            <IconButton
                              color="inherit"
                              aria-label="open drawer"
                              onClick={() =>
                                this.setState(({ open }) => ({
                                  open: !open
                                }))
                              }
                              className={classes.menuButton}
                            >
                              <MenuIcon />
                            </IconButton>
                            <SVG className={classes.logo} src={saleorLogo} />
                          </Toolbar>
                          <Toolbar
                            disableGutters
                            className={classes.toolBarContent}
                          >
                            <div className={classes.spacer} />
                            <MenuToggle ariaOwns="user-menu">
                              {({
                                open: menuOpen,
                                actions: { open: openMenu, close: closeMenu }
                              }) => {
                                const handleLogout = () => {
                                  close();
                                  logout();
                                };
                                return (
                                  <>
                                    <div
                                      className={classes.email}
                                      ref={this.anchor}
                                      onClick={!menuOpen ? openMenu : undefined}
                                    >
                                      <Hidden smDown>
                                        <Typography
                                          className={classes.emailLabel}
                                          component="span"
                                          variant="subheading"
                                        >
                                          {user.email}
                                        </Typography>
                                        <ArrowDropdown
                                          className={classNames({
                                            [classes.arrow]: true,
                                            [classes.rotate]: menuOpen
                                          })}
                                        />
                                      </Hidden>
                                      <Hidden mdUp>
                                        <IconButton
                                          className={classes.userIcon}
                                        >
                                          <Person />
                                        </IconButton>
                                      </Hidden>
                                    </div>
                                    <Popper
                                      open={menuOpen}
                                      anchorEl={this.anchor.current}
                                      transition
                                      disablePortal
                                      placement="bottom-end"
                                    >
                                      {({ TransitionProps, placement }) => (
                                        <Grow
                                          {...TransitionProps}
                                          style={{
                                            minWidth: "10rem",
                                            transformOrigin:
                                              placement === "bottom"
                                                ? "right top"
                                                : "right bottom"
                                          }}
                                        >
                                          <Paper>
                                            <ClickAwayListener
                                              onClickAway={closeMenu}
                                              mouseEvent="onClick"
                                            >
                                              <Menu>
                                                <MenuItem
                                                  className={
                                                    classes.userMenuItem
                                                  }
                                                  onClick={handleLogout}
                                                >
                                                  {i18n.t("Log out", {
                                                    context: "button"
                                                  })}
                                                </MenuItem>
                                              </Menu>
                                            </ClickAwayListener>
                                          </Paper>
                                        </Grow>
                                      )}
                                    </Popper>
                                  </>
                                );
                              }}
                            </MenuToggle>
                          </Toolbar>
                          {isProgressVisible && (
                            <LinearProgress
                              className={classes.appLoader}
                              color="secondary"
                            />
                          )}
                        </AppBar>
                        <ResponsiveDrawer
                          onClose={this.closeDrawer}
                          open={open}
                        >
                          <div className={classes.menuList}>
                            <MenuList
                              menuItems={menuStructure}
                              user={user}
                              onMenuItemClick={handleMenuItemClick}
                            />
                            <div className={classes.spacer} />
                            {configurationMenu.filter(menuItem =>
                              user.permissions
                                .map(perm => perm.code)
                                .includes(menuItem.permission)
                            ).length > 0 && (
                              <a
                                className={classes.menuListItem}
                                href={removeDoubleSlashes(
                                  appMountPoint + configurationMenuUrl
                                )}
                                onClick={event =>
                                  handleMenuItemClick(
                                    configurationMenuUrl,
                                    event
                                  )
                                }
                              >
                                <SettingsIcon />
                                <Typography
                                  aria-label="configure"
                                  className={classes.menuListItemText}
                                >
                                  {i18n.t("Configure")}
                                </Typography>
                              </a>
                            )}
                          </div>
                        </ResponsiveDrawer>
                        <main className={classes.content}>{children}</main>
                      </div>
                    );
                  }}
                </Navigator>
              )}
            </UserContext.Consumer>
          )}
        </AppProgress>
      );
    }
  }
);

export default AppRoot;
