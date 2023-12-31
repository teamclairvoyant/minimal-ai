import { alpha, styled } from "@mui/material/styles";
import { Box, Stack, AppBar, Toolbar, Typography } from "@mui/material";
import AccountPopover from "../../components/AccountPopover";
import NotificationsPopover from "../../components/NotificationsPopover";
import Logo from "../../components/Logo";

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
  [theme.breakpoints.up('lg')]: {
    minHeight: APPBAR_DESKTOP,
    padding: theme.spacing(0, 5)
  }
}));


export default function Navbar({ title }) {
  return (
    <RootStyle>
      <ToolbarStyle>
        <Logo />
        <Box sx={{ flexGrow: 1 }}>
          {title && <Stack 
            paddingLeft={2} 
            marginLeft={2}
            sx={{
              borderLeft: 1,
              color: "rgb(243, 242, 241)"
            }}
            >
            <Typography variant="h6" color={"black"}>
              {title}
            </Typography>
          </Stack>
          }
        </Box>
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
