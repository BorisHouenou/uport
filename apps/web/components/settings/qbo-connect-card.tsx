"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Link2, Link2Off, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";

function useQBOStatus() {
  return useQuery({
    queryKey: ["qbo-status"],
    queryFn: () => apiClient.get("/integrations/qbo/status").then(r => r.data),
  });
}

function useQBOConnect() {
  return useMutation({
    mutationFn: () => apiClient.get("/integrations/qbo/connect").then(r => r.data),
  });
}

function useQBODisconnect() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post("/integrations/qbo/disconnect").then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["qbo-status"] });
      toast.success("QuickBooks disconnected");
    },
  });
}

export function QBOConnectCard() {
  const { data: status, isLoading } = useQBOStatus();
  const connect = useQBOConnect();
  const disconnect = useQBODisconnect();
  const [importCount, setImportCount] = useState<number | null>(null);

  const handleConnect = async () => {
    try {
      const { auth_url } = await connect.mutateAsync();
      window.location.href = auth_url;
    } catch {
      toast.error("Failed to initiate QuickBooks connection");
    }
  };

  const handlePreview = async () => {
    try {
      const { count } = await apiClient.get("/integrations/qbo/items").then(r => r.data);
      setImportCount(count);
      toast.success(`Found ${count} items in QuickBooks`);
    } catch {
      toast.error("Failed to fetch QuickBooks items");
    }
  };

  const connected = status?.connected ?? false;

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CardTitle>QuickBooks Online</CardTitle>
            {connected ? (
              <Badge className="bg-green-100 text-green-800">Connected</Badge>
            ) : (
              <Badge variant="secondary">Not connected</Badge>
            )}
          </div>
          <CardDescription className="mt-1">
            Import your product catalog and BOM lines directly from QuickBooks.
            Items are automatically classified by HS code using AI.
          </CardDescription>
        </div>
        {/* QBO Logo placeholder */}
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#2CA01C] text-white font-bold text-sm">
          QB
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {connected ? (
          <>
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              Connected to realm: <span className="font-mono text-xs">{status?.realm_id}</span>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" onClick={handlePreview}>
                <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                Preview items
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="text-red-600 hover:border-red-300 hover:bg-red-50"
                onClick={() => disconnect.mutate()}
                loading={disconnect.isPending}
              >
                <Link2Off className="mr-1.5 h-3.5 w-3.5" />
                Disconnect
              </Button>
            </div>

            {importCount !== null && (
              <p className="text-xs text-slate-500">
                {importCount} active items found. Use the BOM page to import them into a product.
              </p>
            )}
          </>
        ) : (
          <Button onClick={handleConnect} loading={connect.isPending}>
            <Link2 className="mr-1.5 h-4 w-4" />
            Connect QuickBooks
          </Button>
        )}

        <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-500">
          <strong>What gets imported:</strong> Inventory items, service items, and purchased goods.
          HS codes are classified automatically. Supplier country must be set manually or via declarations.
        </div>
      </CardContent>
    </Card>
  );
}
