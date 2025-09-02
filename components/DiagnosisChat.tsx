import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { ScrollArea } from './ui/scroll-area';
import { Alert, AlertDescription } from './ui/alert';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Send, Paperclip, Bot, User, AlertTriangle } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  image?: File;
}

interface DiagnosisStage {
  stage: 'initial' | 'followup' | 'diagnosis';
  symptoms: Array<{
    name: string;
    severity: number;
    duration: string;
  }>;
}

export function DiagnosisChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'bot',
      content: "Hello! I'm your AI medical assistant. I'll help you understand your symptoms better. Please describe your main symptoms, and I'll ask follow-up questions to narrow down possible conditions.",
      timestamp: new Date()
    }
  ]);
  
  const [userInput, setUserInput] = useState('');
  const [attachedImage, setAttachedImage] = useState<File | null>(null);
  const [diagnosisState, setDiagnosisState] = useState<DiagnosisStage>({
    stage: 'initial',
    symptoms: []
  });
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleFileAttach = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setAttachedImage(file);
    }
  };

  const generateFollowupQuestion = () => {
    const questions = [
      "How long have you been experiencing these symptoms?",
      "On a scale of 1-10, how would you rate the severity of your symptoms?",
      "Do you have any fever or temperature changes?",
      "Have you experienced any nausea or vomiting?",
      "Are you taking any medications currently?",
      "Do you have any known allergies or medical conditions?",
      "Have you traveled recently or been exposed to anyone who was sick?"
    ];
    return questions[Math.floor(Math.random() * questions.length)];
  };

  const generateDiagnosis = () => {
    const diagnoses = [
      {
        condition: "Upper Respiratory Infection",
        confidence: "85%",
        description: "Common cold or flu-like symptoms",
        recommendations: [
          "Rest and stay hydrated",
          "Consider over-the-counter pain relievers",
          "Monitor symptoms for 7-10 days",
          "Seek medical attention if symptoms worsen"
        ]
      },
      {
        condition: "Seasonal Allergies",
        confidence: "70%",
        description: "Allergic reaction to environmental factors",
        recommendations: [
          "Avoid known allergens",
          "Consider antihistamines",
          "Use air purifiers indoors",
          "Consult an allergist if symptoms persist"
        ]
      },
      {
        condition: "Mild Gastroenteritis",
        confidence: "75%",
        description: "Stomach flu or food-related illness",
        recommendations: [
          "Stay hydrated with clear fluids",
          "Follow the BRAT diet (Bananas, Rice, Applesauce, Toast)",
          "Rest and avoid solid foods temporarily",
          "Seek medical care if symptoms persist over 3 days"
        ]
      }
    ];

    const diagnosis = diagnoses[Math.floor(Math.random() * diagnoses.length)];
    
    let response = `Based on your symptoms, here's my assessment:\n\n`;
    response += `**Likely Condition:** ${diagnosis.condition}\n`;
    response += `**Confidence Level:** ${diagnosis.confidence}\n\n`;
    response += `**Description:** ${diagnosis.description}\n\n`;
    response += `**Recommendations:**\n`;
    
    diagnosis.recommendations.forEach(rec => {
      response += `• ${rec}\n`;
    });
    
    response += `\n⚠️ **Important:** This is an AI assessment only. Please consult with a healthcare professional for proper diagnosis and treatment.\n\nWould you like to start a new consultation or check a prescription?`;
    
    return response;
  };

  const handleSendMessage = () => {
    if (!userInput.trim() && !attachedImage) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userInput,
      timestamp: new Date(),
      image: attachedImage || undefined
    };

    setMessages(prev => [...prev, userMessage]);

    // Process based on diagnosis stage
    let botResponse = '';
    
    if (diagnosisState.stage === 'initial') {
      const symptom = {
        name: userInput,
        severity: 5,
        duration: 'recent'
      };
      
      setDiagnosisState({
        stage: 'followup',
        symptoms: [symptom]
      });
      
      botResponse = generateFollowupQuestion();
      
    } else if (diagnosisState.stage === 'followup') {
      const symptom = {
        name: userInput,
        severity: 5,
        duration: 'recent'
      };
      
      const newSymptoms = [...diagnosisState.symptoms, symptom];
      
      if (newSymptoms.length >= 3) {
        setDiagnosisState({
          stage: 'diagnosis',
          symptoms: newSymptoms
        });
        botResponse = generateDiagnosis();
      } else {
        setDiagnosisState({
          ...diagnosisState,
          symptoms: newSymptoms
        });
        botResponse = generateFollowupQuestion();
      }
      
    } else {
      if (userInput.toLowerCase().includes('new') || userInput.toLowerCase().includes('start')) {
        setDiagnosisState({
          stage: 'initial',
          symptoms: []
        });
        botResponse = "Let's start a new consultation. Please describe your main symptoms.";
      } else {
        botResponse = "I can help you with symptom analysis. Type 'new consultation' to start over, or switch to the Prescription Checker tab if you need prescription validation.";
      }
    }

    // Add bot response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: botResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);

    // Reset input
    setUserInput('');
    setAttachedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          AI Diagnosis Assistant
        </CardTitle>
        <CardDescription>
          Describe your symptoms and I'll help narrow down possible conditions
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Chat Messages */}
        <ScrollArea 
          ref={scrollAreaRef}
          className="h-[400px] w-full rounded-md border p-4 space-y-4 scroll-area-viewport"
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 message-animate ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-muted text-muted-foreground'
                }`}>
                  {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                
                <div className={`rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}>
                  <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                  
                  {message.image && (
                    <div className="mt-2">
                      <ImageWithFallback
                        src={URL.createObjectURL(message.image)}
                        alt="User uploaded image"
                        className="max-w-[200px] rounded-md"
                      />
                    </div>
                  )}
                  
                  <div className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </ScrollArea>

        {/* Input Area */}
        <div className="space-y-3">
          {attachedImage && (
            <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
              <ImageWithFallback
                src={URL.createObjectURL(attachedImage)}
                alt="Attached image"
                className="w-12 h-12 object-cover rounded"
              />
              <span className="text-sm text-muted-foreground">{attachedImage.name}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAttachedImage(null)}
                className="ml-auto"
              >
                ×
              </Button>
            </div>
          )}
          
          <div className="flex gap-2">
            <Textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Describe your symptoms..."
              className="flex-1 min-h-[80px] resize-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            
            <div className="flex flex-col gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleFileAttach}
                className="h-10 w-10 p-0 file-upload-zone"
                title="Attach image"
              >
                <Paperclip className="h-4 w-4" />
              </Button>
              
              <Button
                onClick={handleSendMessage}
                disabled={!userInput.trim() && !attachedImage}
                className="h-10 w-10 p-0"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Warning Notice */}
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>Medical Disclaimer:</strong> This AI assistant provides informational support only 
            and should not replace professional medical advice, diagnosis, or treatment. Always consult 
            qualified healthcare providers for medical concerns.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
}