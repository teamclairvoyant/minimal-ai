import { Stack, Typography } from "@mui/material";
import { pipelineStore } from "../appState/pipelineStore";


function PipelineDetails() {
    const [{ pipeline }, ] = pipelineStore()
    return (
    <Stack spacing={2}>
        <Stack direction="row" spacing={2} sx={{alignItems: "center",justifyContent: "space-between"}}>
            <Typography variant="h4" align="center" sx={{ mb: 5 }}>Pipeline :</Typography>
            <Typography variant="h6" align="center" sx={{ mb: 5 }}>{pipeline.name}</Typography>
        </Stack>
        <Stack direction="row" spacing={2} sx={{alignItems: "center",justifyContent: "space-between"}}>
            <Typography variant="h4" align="center" sx={{ mb: 5 }}>Status :</Typography>
            <Typography variant="h6" align="center" sx={{ mb: 5 }}>{pipeline.status}</Typography>
        </Stack>
    </Stack>
    )
}

export default PipelineDetails