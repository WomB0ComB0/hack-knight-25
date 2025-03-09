'use client'

import { SignUp } from "@clerk/nextjs"
import { dark } from "@clerk/themes"
import { useTheme } from "next-themes"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function ClerkSignUpForm() {
  const { theme } = useTheme()

  return (
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-xl">Sign Up</CardTitle>
        <CardDescription>
          Enter your information to create an account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <SignUp 
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
              card: "bg-transparent shadow-none",
            },
          }}
        />
      </CardContent>
    </Card>
  )
}