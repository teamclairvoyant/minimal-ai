import { styled } from "@mui/material/styles";
import { Box, Grid, Stack, Typography } from "@mui/material";
import PropTypes from "prop-types";
import AppMenu from "../../components/appMenu";


const RootStyle = styled('div')(() => ({
  borderBottom: "1px solid grey",
  height: 50,
  display: "flex",
  alignItems: "center",
  paddingLeft: 20,
  paddingRight: 20
}));

SubBar.propTypes = {
  onButtonClick: PropTypes.func
}

export default function SubBar({ onButtonClick }) {
  return (
    <Grid
      container
      direction={"row"}
      justifyContent={"center"}
      paddingLeft={4}
      alignItems={"center"}
      sx={{
        height: 48
      }}>
      <Stack
        direction={"row"}
        spacing={2}
      >
        <AppMenu menuName={"Source"} type={"input"} iconName={"material-symbols:add-circle"} buttonColor={"#4e969f"} addNode={onButtonClick}></AppMenu>
        <AppMenu menuName={"Transform"} type={"default"} iconName={"tabler:transform-filled"} buttonColor={"#7a20d1"} addNode={onButtonClick}></AppMenu>
        <AppMenu menuName={"Target"} type={"output"} iconName={"material-symbols:cloud-download-rounded"} buttonColor={"#489f4e"} addNode={onButtonClick}></AppMenu>
      </Stack>
      {/* <Stack /> */}
    </Grid>
  );
}
