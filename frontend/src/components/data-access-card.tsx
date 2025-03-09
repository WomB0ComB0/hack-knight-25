import { Lock, Shield, UserCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function DataAccessCard() {
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
          <div className="flex items-start gap-3 rounded-lg border p-3">
            <UserCheck className="mt-1 h-5 w-5 text-green-500" />
            <div>
              <h3 className="font-medium">Dr. Jacob Jones</h3>
              <p className="text-sm text-gray-500">Primary Care Physician</p>
              <div className="mt-1 flex items-center gap-1 text-xs text-green-600">
                <Shield className="h-3 w-3" />
                <span>Full access granted</span>
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-lg border p-3">
            <UserCheck className="mt-1 h-5 w-5 text-green-500" />
            <div>
              <h3 className="font-medium">Dr. Theresa Webb</h3>
              <p className="text-sm text-gray-500">Psychiatrist</p>
              <div className="mt-1 flex items-center gap-1 text-xs text-green-600">
                <Shield className="h-3 w-3" />
                <span>Limited access (Mental health records only)</span>
              </div>
            </div>
          </div>
          <div className="flex items-start gap-3 rounded-lg border p-3">
            <UserCheck className="mt-1 h-5 w-5 text-yellow-500" />
            <div>
              <h3 className="font-medium">City Hospital Lab</h3>
              <p className="text-sm text-gray-500">Laboratory</p>
              <div className="mt-1 flex items-center gap-1 text-xs text-yellow-600">
                <Shield className="h-3 w-3" />
                <span>Pending approval (Lab results only)</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">Manage Data Access</Button>
      </CardFooter>
    </Card>
  );
}
