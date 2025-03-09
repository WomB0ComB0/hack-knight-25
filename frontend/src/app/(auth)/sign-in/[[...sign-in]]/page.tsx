'use client'

import { SignIn } from "@clerk/nextjs"
import { dark } from "@clerk/themes"
import { useTheme } from "next-themes"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ClerkLoginForm() {
  const { theme } = useTheme()

  return (
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-2xl">Login</CardTitle>
        <CardDescription>
          Sign in to your account to continue
        </CardDescription>
      </CardHeader>
      <CardContent>
        <SignIn 
          appearance={{
            baseTheme: theme === "dark" ? dark : undefined,
            elements: {
              formButtonPrimary: 
                "bg-primary text-primary-foreground hover:bg-primary/90",
              socialButtonsBlockButton: 
                "bg-secondary text-secondary-foreground hover:bg-secondary/80",
              formFieldInput: 
                "bg-background text-foreground",
              footerActionLink: 
                "text-primary hover:text-primary/80",
            },
          }}
        />
      </CardContent>
    </Card>
  )
}