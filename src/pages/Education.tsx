import {
    AcademicCapIcon,
    BookOpenIcon,
    ChartBarIcon,
    CheckCircleIcon,
    ClockIcon,
    CurrencyDollarIcon,
    LightBulbIcon,
    QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import { motion } from 'framer-motion';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useQuery } from 'react-query';

const API_BASE_URL = 'http://localhost:8001';

interface EducationModule {
  id: number;
  title: string;
  description: string;
  content: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  duration: string;
  category: string;
  quiz?: {
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
  }[];
}

interface QuizAnswer {
  moduleId: number;
  questionIndex: number;
  selectedAnswer: number;
}

const Education = () => {
  const [selectedModule, setSelectedModule] = useState<EducationModule | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [quizAnswers, setQuizAnswers] = useState<QuizAnswer[]>([]);
  const [showQuizResults, setShowQuizResults] = useState<boolean>(false);

  // Fetch education modules
  const { data: modulesData, isLoading: modulesLoading } = useQuery<{modules: EducationModule[]}>(
    'education-modules',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/api/education/modules`);
      return response.data;
    },
    {
      onError: () => toast.error('Failed to load education modules')
    }
  );

  const categories = ['all', 'stocks', 'portfolio', 'risk', 'crypto', 'fundamentals'];

  const filteredModules = modulesData?.modules?.filter(module => 
    selectedCategory === 'all' || module.category === selectedCategory
  ) || [];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-400 bg-green-500/20 border-green-500/30';
      case 'Intermediate': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'Advanced': return 'text-red-400 bg-red-500/20 border-red-500/30';
      default: return 'text-primary-200 bg-primary-800/20 border-primary-700/30';
    }
  };

  const handleQuizAnswer = (moduleId: number, questionIndex: number, selectedAnswer: number) => {
    setQuizAnswers(prev => {
      const existing = prev.filter(a => !(a.moduleId === moduleId && a.questionIndex === questionIndex));
      return [...existing, { moduleId, questionIndex, selectedAnswer }];
    });
  };

  const calculateQuizScore = (module: EducationModule) => {
    if (!module.quiz) return 0;
    
    const moduleAnswers = quizAnswers.filter(a => a.moduleId === module.id);
    const correctAnswers = moduleAnswers.filter(answer => {
      const question = module.quiz![answer.questionIndex];
      return question && answer.selectedAnswer === question.correct_answer;
    });
    
    return Math.round((correctAnswers.length / module.quiz.length) * 100);
  };

  const submitQuiz = () => {
    setShowQuizResults(true);
    const score = selectedModule ? calculateQuizScore(selectedModule) : 0;
    toast.success(`Quiz completed! Your score: ${score}%`);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-primary-50 mb-2">
          Financial Education Center
        </h1>
        <p className="text-lg text-primary-100/80">
          Master financial markets with interactive lessons and practical knowledge
        </p>
      </motion.div>

      {/* Category Filter */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
      >
        <h2 className="text-xl font-semibold text-primary-50 mb-4">Learning Categories</h2>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm transition-colors border ${
                selectedCategory === category
                  ? 'bg-accent-emerald text-white border-accent-emerald'
                  : 'bg-primary-900/30 text-primary-200 border-primary-800/20 hover:border-accent-emerald/30'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </motion.section>

      {/* Module Grid */}
      {!selectedModule ? (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {modulesLoading ? (
            [...Array(6)].map((_, i) => (
              <div key={i} className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 animate-pulse">
                <div className="h-6 bg-primary-800 rounded mb-3"></div>
                <div className="h-4 bg-primary-800 rounded mb-2"></div>
                <div className="h-4 bg-primary-800 rounded w-3/4"></div>
              </div>
            ))
          ) : (
            filteredModules.map((module) => (
              <motion.div
                key={module.id}
                whileHover={{ scale: 1.02 }}
                onClick={() => setSelectedModule(module)}
                className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg hover:border-accent-emerald/30 transition-all cursor-pointer"
              >
                <div className="flex items-start justify-between mb-3">
                  <BookOpenIcon className="h-8 w-8 text-accent-emerald flex-shrink-0" />
                  <div className={`px-2 py-1 rounded text-xs border ${getDifficultyColor(module.difficulty)}`}>
                    {module.difficulty}
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-primary-50 mb-2">{module.title}</h3>
                <p className="text-primary-200 text-sm mb-4">{module.description}</p>
                
                <div className="flex items-center justify-between text-primary-400 text-sm">
                  <div className="flex items-center">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {module.duration}
                  </div>
                  <div className="capitalize">{module.category}</div>
                </div>
              </motion.div>
            ))
          )}
        </motion.section>
      ) : (
        /* Module Detail View */
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          {/* Module Header */}
          <div className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => {
                  setSelectedModule(null);
                  setQuizAnswers([]);
                  setShowQuizResults(false);
                }}
                className="text-accent-emerald hover:text-primary-300 transition-colors"
              >
                ← Back to Modules
              </button>
              <div className={`px-3 py-1 rounded border ${getDifficultyColor(selectedModule.difficulty)}`}>
                {selectedModule.difficulty}
              </div>
            </div>
            
            <h1 className="text-3xl font-bold text-primary-50 mb-2">{selectedModule.title}</h1>
            <p className="text-primary-200 mb-4">{selectedModule.description}</p>
            
            <div className="flex items-center gap-4 text-primary-400 text-sm">
              <div className="flex items-center">
                <ClockIcon className="h-4 w-4 mr-1" />
                {selectedModule.duration}
              </div>
              <div className="flex items-center">
                <AcademicCapIcon className="h-4 w-4 mr-1" />
                {selectedModule.category}
              </div>
            </div>
          </div>

          {/* Module Content */}
          <div className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg">
            <h2 className="text-2xl font-semibold text-primary-50 mb-4 flex items-center">
              <BookOpenIcon className="h-6 w-6 mr-2 text-accent-emerald" />
              Learning Material
            </h2>
            <div className="prose prose-invert max-w-none">
              <div 
                className="text-primary-200 leading-relaxed whitespace-pre-line"
                dangerouslySetInnerHTML={{ __html: selectedModule.content }}
              />
            </div>
          </div>

          {/* Quiz Section */}
          {selectedModule.quiz && selectedModule.quiz.length > 0 && (
            <div className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg">
              <h2 className="text-2xl font-semibold text-primary-50 mb-4 flex items-center">
                <QuestionMarkCircleIcon className="h-6 w-6 mr-2 text-accent-emerald" />
                Knowledge Quiz
              </h2>
              
              <div className="space-y-6">
                {selectedModule.quiz.map((question, questionIndex) => (
                  <div key={questionIndex} className="bg-primary-900/30 rounded-lg p-5 border border-primary-800/20">
                    <h3 className="text-lg font-semibold text-primary-50 mb-4">
                      Question {questionIndex + 1}: {question.question}
                    </h3>
                    
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => {
                        const userAnswer = quizAnswers.find(a => 
                          a.moduleId === selectedModule.id && a.questionIndex === questionIndex
                        );
                        const isSelected = userAnswer?.selectedAnswer === optionIndex;
                        const isCorrect = optionIndex === question.correct_answer;
                        
                        return (
                          <button
                            key={optionIndex}
                            onClick={() => handleQuizAnswer(selectedModule.id, questionIndex, optionIndex)}
                            disabled={showQuizResults}
                            className={`w-full text-left p-3 rounded-lg border transition-colors ${
                              showQuizResults
                                ? isCorrect
                                  ? 'bg-green-500/20 border-green-500/30 text-green-400'
                                  : isSelected
                                  ? 'bg-red-500/20 border-red-500/30 text-red-400'
                                  : 'bg-primary-800/20 border-primary-700/20 text-primary-300'
                                : isSelected
                                ? 'bg-accent-emerald/20 border-accent-emerald/30 text-accent-emerald'
                                : 'bg-primary-800/20 border-primary-700/20 text-primary-200 hover:border-accent-emerald/30'
                            }`}
                          >
                            <div className="flex items-center">
                              {showQuizResults && isCorrect && (
                                <CheckCircleIcon className="h-5 w-5 mr-2 text-green-400" />
                              )}
                              {showQuizResults && isSelected && !isCorrect && (
                                <QuestionMarkCircleIcon className="h-5 w-5 mr-2 text-red-400" />
                              )}
                              {option}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                    
                    {showQuizResults && (
                      <div className="mt-4 p-3 bg-accent-emerald/10 border border-accent-emerald/20 rounded-lg">
                        <p className="text-primary-200 text-sm">
                          <LightBulbIcon className="h-4 w-4 inline mr-1 text-accent-emerald" />
                          <strong>Explanation:</strong> {question.explanation}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
                
                <div className="flex justify-between items-center">
                  <div className="text-primary-400 text-sm">
                    {quizAnswers.filter(a => a.moduleId === selectedModule.id).length} of {selectedModule.quiz.length} questions answered
                  </div>
                  
                  {!showQuizResults ? (
                    <button
                      onClick={submitQuiz}
                      disabled={quizAnswers.filter(a => a.moduleId === selectedModule.id).length !== selectedModule.quiz.length}
                      className="px-6 py-2 bg-accent-emerald hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Submit Quiz
                    </button>
                  ) : (
                    <div className="text-right">
                      <p className="text-lg font-semibold text-primary-50">
                        Your Score: {calculateQuizScore(selectedModule)}%
                      </p>
                      <p className="text-primary-400 text-sm">
                        {calculateQuizScore(selectedModule) >= 80 ? 'Excellent work! 🎉' :
                         calculateQuizScore(selectedModule) >= 60 ? 'Good job! 👍' :
                         'Keep learning! 📚'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </motion.section>
      )}

      {/* Learning Resources */}
      {!selectedModule && (
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-card-gradient rounded-xl p-6 border border-primary-800/30 shadow-lg"
        >
          <h2 className="text-2xl font-semibold text-primary-50 mb-4">Learning Tips</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-accent-emerald/10 border border-accent-emerald/20 rounded-lg">
              <ChartBarIcon className="h-8 w-8 text-accent-emerald mb-3" />
              <h3 className="text-accent-emerald font-semibold mb-2">Start with Basics</h3>
              <p className="text-primary-200 text-sm">
                Begin with fundamental concepts before moving to advanced topics. Build a solid foundation.
              </p>
            </div>
            <div className="p-4 bg-primary-800/30 border border-primary-700/20 rounded-lg">
              <CurrencyDollarIcon className="h-8 w-8 text-yellow-400 mb-3" />
              <h3 className="text-yellow-400 font-semibold mb-2">Practice Regularly</h3>
              <p className="text-primary-200 text-sm">
                Apply your knowledge with our interactive tools and real market data analysis.
              </p>
            </div>
            <div className="p-4 bg-primary-800/30 border border-primary-700/20 rounded-lg">
              <LightBulbIcon className="h-8 w-8 text-blue-400 mb-3" />
              <h3 className="text-blue-400 font-semibold mb-2">Stay Updated</h3>
              <p className="text-primary-200 text-sm">
                Financial markets evolve constantly. Keep learning and stay informed about new trends.
              </p>
            </div>
          </div>
        </motion.section>
      )}
    </div>
  );
};

export default Education; 