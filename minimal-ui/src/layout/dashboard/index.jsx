import { Grid, Container, Typography } from '@mui/material';
import Page from '../../components/Page';
import AppWidgetSummary from '../../sections/AppWidgetSummary';
import TasksTable from '../../sections/TasksTable';
import { useState, useEffect } from 'react';
import { backendApi } from '../../api/api';

const DUMMY = {"total_pipelines":2,"scheduled_count":3,"successful_count":4,"failed_count":1};

export default function WorkbookHome() {
  const [summary, setSummary] = useState(DUMMY);

  useEffect(() => {
    async function getSummary() {
      const response = await backendApi.get("/api/v1/summary");
      if (response.data) {
        setSummary(response.data.summary);
      }
    }
    getSummary();
  }, []);

  if (!summary) return "No Data To Show"

  return (
    <Page title="Dashboard">
      <Container maxWidth="xl">
        <Typography variant="h4" align="center" sx={{ mb: 5 }}>
          Hi, Welcome back
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Total tasks" total={summary['total_pipelines']} icon={'eos-icons:background-tasks'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Scheduled tasks" total={summary['scheduled_count']} color="info" icon={'material-symbols:schedule-outline-rounded'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Successful run" total={summary['successful_count']} color="success" icon={'icon-park-outline:success'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Failed" total={summary['failed_count']} color="error" icon={'ant-design:bug-filled'} />
          </Grid>
        </Grid>

        <Grid item xs={12} md={6} lg={8}>
          <TasksTable />
        </Grid>
      </Container>
    </Page>
  );
}
