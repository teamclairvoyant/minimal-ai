import { AppBar, Stack, Toolbar } from "@mui/material";
import { alpha, styled } from "@mui/material/styles";
import AccountPopover from "../../components/AccountPopover";
import Logo from "../../components/Logo";
import NotificationsPopover from "../../components/NotificationsPopover";

const DRAWER_WIDTH = 0;
const APPBAR_MOBILE = 32;
const APPBAR_DESKTOP = 64;

const RootStyle = styled(AppBar)(({ theme }) => ({
  boxShadow: 'none',
  backdropFilter: 'blur(6px)',
  WebkitBackdropFilter: 'blur(6px)',
  backgroundColor: alpha(theme.palette.background.default, 0.72),
  borderBottom: "1px solid grey",
  [theme.breakpoints.up('lg')]: {
    width: `calc(100% - ${DRAWER_WIDTH + 1}px)`
  }
}));

const ToolbarStyle = styled(Toolbar)(({ theme }) => ({
  minHeight: APPBAR_MOBILE,
  display: "flex",
  justifyContent: "space-between",
  [theme.breakpoints.up('lg')]: {
    minHeight: APPBAR_DESKTOP,
    padding: theme.spacing(0, 5)
  }
}));


export default function Navbar() {
  return (
    <RootStyle>
      <ToolbarStyle>
        <Logo />
        <Stack
          direction="row"
          alignItems="center"
          spacing={{ xs: 0.5, sm: 1.5 }}
        >
          <NotificationsPopover />
          <AccountPopover />
        </Stack>
      </ToolbarStyle>
    </RootStyle>
  );
}
