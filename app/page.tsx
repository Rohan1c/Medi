"use client";
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Moon, Sun, Stethoscope } from 'lucide-react';
import { DiagnosisChat } from '../components/DiagnosisChat';
import { PrescriptionChecker } from '../components/PrescriptionChecker';

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={`min-h-screen bg-background text-foreground transition-colors duration-200`}>
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary text-primary-foreground p-2 rounded-lg">
                <Stethoscope className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">MedValidator AI</h1>
                <p className="text-sm text-muted-foreground">AI-Powered Medical Assistant</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={toggleTheme}
              className="rounded-full"
            >
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="diagnosis" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 max-w-md mx-auto">
            <TabsTrigger value="diagnosis" className="flex items-center gap-2">
              <Stethoscope className="h-4 w-4" />
              Diagnosis Assistant
            </TabsTrigger>
            <TabsTrigger value="prescription" className="flex items-center gap-2">
              📋 Prescription Checker
            </TabsTrigger>
          </TabsList>

          <TabsContent value="diagnosis">
            <DiagnosisChat />
          </TabsContent>

          <TabsContent value="prescription">
            <PrescriptionChecker />
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <footer className="mt-12 pt-8 border-t border-border">
          <div className="text-center text-sm text-muted-foreground">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-destructive">⚠️</span>
              <span className="font-medium">Medical Disclaimer</span>
            </div>
            <p>
              This AI assistant tool provides informational support only and should not replace 
              professional medical advice, diagnosis, or treatment. Always consult with qualified 
              healthcare professionals for medical concerns.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}