import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface RankingTableProps {
  llms: {
    llmName: string;
    score: number;
    positive: number;
    negative: number;
    neutral: number;
  }[];
}

export function RankingTable({ llms }: RankingTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">Rank</TableHead>
          <TableHead>LLM</TableHead>
          <TableHead>Score</TableHead>
          <TableHead>Total Reviews</TableHead>
          <TableHead>Positive</TableHead>
          <TableHead>Negative</TableHead>
          <TableHead>Neutral</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {llms.map((llm, index) => (
          <TableRow key={llm.llmName}>
            <TableCell>{index + 1}</TableCell>
            <TableCell>{llm.llmName}</TableCell>
            <TableCell>{llm.score.toFixed(3)}</TableCell>
            <TableCell>{llm.positive + llm.negative + llm.neutral}</TableCell>
            <TableCell>{llm.positive}</TableCell>
            <TableCell>{llm.negative}</TableCell>
            <TableCell>{llm.neutral}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
