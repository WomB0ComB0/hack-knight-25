"use client";

import { useState, useEffect } from "react";
import { Clock, Database, GitBranchPlus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/utils/api";
import { toast } from "@/components/ui/use-toast";

interface BlockchainInfo {
  length: number;
  chain: Array<{
    index: number;
    timestamp: number;
    transactions: Array<any>;
    previous_hash: string;
  }>;
}

interface PendingTransactions {
  count: number;
  pending_transactions: Array<any>;
}

export function BlockchainInfoCard() {
  const [blockchainInfo, setBlockchainInfo] = useState<BlockchainInfo | null>(null);
  const [pendingTransactions, setPendingTransactions] = useState<PendingTransactions | null>(null);
  const [loading, setLoading] = useState(false);
  const [miningLoading, setMiningLoading] = useState(false);

  const fetchBlockchainData = async () => {
    try {
      setLoading(true);
      const chainData = await api.getBlockchainInfo<BlockchainInfo>();
      setBlockchainInfo(chainData);

      const pendingTxData = await api.getPendingTransactions<PendingTransactions>();
      setPendingTransactions(pendingTxData);
    } catch (error) {
      console.error("Error fetching blockchain data:", error);
      toast({
        title: "Error",
        description: "Failed to fetch blockchain data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleMineBlock = async () => {
    try {
      setMiningLoading(true);
      await api.mineBlock();
      toast({
        title: "Success",
        description: "New block mined successfully!",
      });
      // Refresh data after mining
      fetchBlockchainData();
    } catch (error) {
      console.error("Error mining block:", error);
      toast({
        title: "Error",
        description: "Failed to mine block",
        variant: "destructive",
      });
    } finally {
      setMiningLoading(false);
    }
  };

  useEffect(() => {
    fetchBlockchainData();
  }, []);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5 text-blue-600" />
          Blockchain Status
        </CardTitle>
        <CardDescription>
          Current state of the healthcare blockchain
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex h-40 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="space-y-4">
            <div className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitBranchPlus className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Chain Length</span>
                </div>
                <span className="text-xl font-bold">
                  {blockchainInfo?.length || 0} blocks
                </span>
              </div>
            </div>

            <div className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Last Updated</span>
                </div>
                <span className="text-sm">
                  {blockchainInfo?.chain[0]
                    ? formatDate(blockchainInfo.chain[0].timestamp)
                    : "N/A"}
                </span>
              </div>
            </div>

            <div className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Pending Transactions</span>
                </div>
                <span className="text-xl font-bold">
                  {pendingTransactions?.count || 0}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button 
          onClick={handleMineBlock} 
          className="w-full"
          disabled={miningLoading}
        >
          {miningLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Mine New Block
        </Button>
      </CardFooter>
    </Card>
  );
}