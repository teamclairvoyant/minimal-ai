import { Outlet } from "react-router-dom";
import { styled } from "@mui/material/styles";
import Navbar from "../navBar";


const APP_BAR_MOBILE = 64;
const APP_BAR_DESKTOP = 92;

const RootStyle = styled('div')({
    display: 'flex',
    minHeight: '100%',
    overflow: 'hidden'
});

const MainStyle = styled('div')(({ theme }) => ({
    flexGrow: 1,
    overflow: 'auto',
    minHeight: '100%',
    paddingTop: APP_BAR_MOBILE + 24,
    paddingBottom: theme.spacing(10),
    [theme.breakpoints.up('lg')]: {
        paddingTop: APP_BAR_DESKTOP,
        
    }
}));



export default function Home() {

  return (
    <RootStyle>
        <Navbar />
        <MainStyle>
          <Outlet />
        </MainStyle>
    </RootStyle>
  );
}
