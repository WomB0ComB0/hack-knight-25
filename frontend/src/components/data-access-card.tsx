"use client";

import { useState, useEffect } from "react";
import { Lock, Shield, UserCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api, auth } from "@/utils/api";
import { toast } from "@/components/ui/use-toast";

export function DataAccessCard() {
  const [accessList, setAccessList] = useState([
    {
      id: "1",
      name: "Dr. Jacob Jones",
      role: "Primary Care Physician",
      status: "approved",
      accessType: "full",
      providerId: "provider123",
    },
    {
      id: "2",
      name: "Dr. Theresa Webb",
      role: "Psychiatrist",
      status: "approved",
      accessType: "limited",
      providerId: "provider456",
      limitations: "Mental health records only",
    },
    {
      id: "3",
      name: "City Hospital Lab",
      role: "Laboratory",
      status: "pending",
      accessType: "limited",
      providerId: "lab789",
      limitations: "Lab results only",
    },
  ]);
  
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    const storedUserData = auth.getUserData();
    if (storedUserData) {
      setUserData(storedUserData);
    }
    
    // In a real app, you would fetch actual access data from the blockchain
    // api.getMedicalRecords(userData?.blockchain_id)
    //   .then(data => {
    //     // Process consents from data
    //     // and update accessList
    //   })
    //   .catch(error => console.error(error));
  }, []);

  const handleManageAccess = () => {
    toast({
      title: "Coming soon",
      description: "Data access management interface will be available soon.",
    });
  };

  const approveAccess = async (providerId: string) => {
    try {
      setLoading(true);
      
      // This would be a real API call in production
      if (userData?.blockchain_id) {
        // await api.manageConsent({
        //   patient_id: userData.blockchain_id,
        //   provider_id: providerId,
        //   access_type: "grant",
        //   signature: "DEBUG_SKIP_VERIFICATION",
        //   record_types: ["diagnostic_report", "lab_result"],
        // });
        
        // Update UI optimistically
        setAccessList(prevList => 
          prevList.map(item => 
            item.providerId === providerId 
              ? { ...item, status: "approved" } 
              : item
          )
        );
        
        toast({
          title: "Access granted",
          description: `Access has been granted to provider ID: ${providerId.substring(0, 8)}...`,
        });
      }
    } catch (error) {
      console.error("Error managing access:", error);
      toast({
        title: "Error",
        description: "Failed to update access permissions",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lock className="h-5 w-5 text-blue-600" />
          Data Access Control
        </CardTitle>
        <CardDescription>
          Manage who can access your medical data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {accessList.map((access) => (
            <div key={access.id} className="flex items-start gap-3 rounded-lg border p-3">
              <UserCheck className={`mt-1 h-5 w-5 ${
                access.status === "approved" ? "text-green-500" : "text-yellow-500"
              }`} />
              <div className="flex-1">
                <h3 className="font-medium">{access.name}</h3>
                <p className="text-sm text-gray-500">{access.role}</p>
                <div className={`mt-1 flex items-center gap-1 text-xs ${
                  access.status === "approved" ? "text-green-600" : "text-yellow-600"
                }`}>
                  <Shield className="h-3 w-3" />
                  <span>
                    {access.status === "approved" 
                      ? `${access.accessType === "full" ? "Full" : "Limited"} access granted${access.limitations ? ` (${access.limitations})` : ''}` 
                      : `Pending approval${access.limitations ? ` (${access.limitations})` : ''}`}
                  </span>
                </div>
              </div>
              {access.status === "pending" && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => approveAccess(access.providerId)}
                  disabled={loading}
                >
                  {loading && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
                  Approve
                </Button>
              )}
            </div>
          ))}
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={handleManageAccess} className="w-full">
          Manage Data Access
        </Button>
      </CardFooter>
    </Card>
  );
}
