import React, { useEffect, useState } from 'react';
import { getPostStats } from '@/lib/database';
import { Table, TableHead, TableRow, TableBody, TableCell } from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const Dashboard = () => {
  const [stats, setStats] = useState<any | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getPostStats();
      setStats(data);
    };
    fetchData();
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="p-4">
      <Card>
        <CardContent>
          <h2 className="text-xl font-bold mb-4">Post Statistics</h2>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Total Posts</TableCell>
                <TableCell>Total Sentiments</TableCell>
                <TableCell>Unique LLMs</TableCell>
                <TableCell>Unique Sentiment Types</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>{stats.totalPosts}</TableCell>
                <TableCell>{stats.totalSentiments}</TableCell>
                <TableCell>{stats.uniqueLLMs}</TableCell>
                <TableCell>{stats.uniqueSentimentTypes}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <Button className="mt-4" onClick={() => window.location.reload()}>Refresh</Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
