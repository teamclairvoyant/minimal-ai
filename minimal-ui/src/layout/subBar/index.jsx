import { styled } from "@mui/material/styles";
import { Box, Stack, Typography} from "@mui/material";
import PropTypes from "prop-types";
import AppMenu from "../../components/appMenu";
import { pipelineStore } from "../../appState/pipelineStore";


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

export default function SubBar({onButtonClick}) {
  const [{pipeline},] = pipelineStore()

  return (
    <RootStyle>
        <Typography variant="subtitle2" sx={{color: "gray"}}>
            current-pipeline : 
        </Typography>
        <Typography variant="subtitle1" sx={{color: "#eb840d"}}>
            &nbsp;{pipeline.name}
        </Typography>
        <Box sx={{ paddingLeft: 30 }} />

        <Stack
          direction="row"
          alignItems="center"
          spacing={{ xs: 0.5, sm: 10 }}
        >
            <AppMenu menuName={"Source"} type={"input"} iconName={"material-symbols:add-circle"} buttonColor={"#4e969f"} addNode={onButtonClick}></AppMenu>
            <AppMenu menuName={"Transform"} type={"default"} iconName={"tabler:transform-filled"} buttonColor={"#7a20d1"} addNode={onButtonClick}></AppMenu>
            <AppMenu menuName={"Target"} type={"output"} iconName={"material-symbols:cloud-download-rounded"} buttonColor={"#489f4e"} addNode={onButtonClick}></AppMenu>
        </Stack>
    </RootStyle>
  );
}
