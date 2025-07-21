import React, { useState } from 'react';
import { QueryProvider } from './providers/QueryProvider';
import { useAppStore } from './stores/appStore';
import { useStories, useStory } from './hooks/useStory';
import { Sidebar } from './components/navigation/Sidebar';
import { SimpleTextEditor } from './components/editors/SimpleTextEditor';
import { Button } from './components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from './components/ui/Card';
import { Menu, X } from 'lucide-react';
import { SNOWFLAKE_STEPS } from './utils/constants';

function AppContent() {
  const { currentStoryId, sidebarCollapsed, setCurrentStory, setSidebarCollapsed } = useAppStore();
  const { data: stories, isLoading: storiesLoading } = useStories();
  const { data: currentStory } = useStory(currentStoryId);
  const [currentStep, setCurrentStep] = useState(1);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // If no story is selected, show story selection
  if (!currentStoryId || !currentStory) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Welcome to Snowflake Method</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Select a story to get started, or create a new one.
            </p>
            
            {storiesLoading ? (
              <p>Loading stories...</p>
            ) : (
              <div className="space-y-2">
                {stories?.stories.map((story) => (
                  <button
                    key={story.story_id}
                    onClick={() => setCurrentStory(story.story_id)}
                    className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <div className="font-medium">{story.slug}</div>
                    <div className="text-sm text-gray-500 truncate">
                      {story.story_idea}
                    </div>
                  </button>
                ))}
                
                {(!stories?.stories.length) && (
                  <p className="text-gray-500 text-center py-4">
                    No stories found. Create your first story!
                  </p>
                )}
                
                <Button className="w-full mt-4">
                  Create New Story
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <Sidebar
        story={currentStory}
        currentStep={currentStep}
        onStepClick={setCurrentStep}
        collapsed={sidebarCollapsed}
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleSidebar}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                {sidebarCollapsed ? (
                  <Menu className="w-5 h-5" />
                ) : (
                  <X className="w-5 h-5" />
                )}
              </button>
              
              <h1 className="text-xl font-semibold text-gray-900">
                Snowflake Method
              </h1>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button variant="secondary" size="sm">
                Stories
              </Button>
              <Button size="sm">
                Export
              </Button>
            </div>
          </div>
        </header>
        
        {/* Main Editor Area */}
        <main className="flex-1 p-6 bg-gray-50 overflow-y-auto">
          <Card>
            <CardHeader>
              <CardTitle>
                Step {currentStep}: {SNOWFLAKE_STEPS.find(s => s.id === currentStep)?.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                {SNOWFLAKE_STEPS.find(s => s.id === currentStep)?.description}
              </p>
              
              {/* Simple editor for Steps 1-2 */}
              {(currentStep === 1 || currentStep === 2) && (
                <SimpleTextEditor
                  content={currentStory.steps[currentStep.toString()] || ''}
                  onChange={(content) => {
                    // For now, just log the change
                    console.log(`Step ${currentStep} content:`, content);
                  }}
                  placeholder={
                    currentStep === 1 
                      ? "Write your story in one sentence..."
                      : "Expand your sentence into a paragraph..."
                  }
                  maxLength={currentStep === 1 ? 200 : 1000}
                />
              )}
              
              {/* Placeholder for other steps */}
              {currentStep > 2 && (
                <p className="text-gray-500 italic">
                  Step {currentStep} editor will be implemented soon.
                </p>
              )}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryProvider>
      <AppContent />
    </QueryProvider>
  );
}

export default App;
