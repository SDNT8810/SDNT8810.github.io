import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { BookOpen, Calendar, Users, ExternalLink } from 'lucide-react';
import { publications } from '../data/content';

const Publications = () => {
  // Group publications by year
  const publicationsByYear = publications.reduce((acc, pub) => {
    if (!acc[pub.year]) {
      acc[pub.year] = [];
    }
    acc[pub.year].push(pub);
    return acc;
  }, {});

  const years = Object.keys(publicationsByYear).sort((a, b) => b - a);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-4xl lg:text-5xl font-bold">Publications</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Research contributions in robotics, control systems, and artificial intelligence
        </p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
        <div className="text-center p-4 bg-muted/30 rounded-lg">
          <div className="text-2xl font-bold text-primary">{publications.length}</div>
          <div className="text-sm text-muted-foreground">Total Publications</div>
        </div>
        <div className="text-center p-4 bg-muted/30 rounded-lg">
          <div className="text-2xl font-bold text-primary">{years.length}</div>
          <div className="text-sm text-muted-foreground">Years Active</div>
        </div>
        <div className="text-center p-4 bg-muted/30 rounded-lg">
          <div className="text-2xl font-bold text-primary">3</div>
          <div className="text-sm text-muted-foreground">Conference Papers</div>
        </div>
        <div className="text-center p-4 bg-muted/30 rounded-lg">
          <div className="text-2xl font-bold text-primary">2</div>
          <div className="text-sm text-muted-foreground">Journal Articles</div>
        </div>
      </div>

      {/* Publications by Year */}
      <div className="space-y-12">
        {years.map(year => (
          <div key={year} className="space-y-6">
            <h2 className="text-2xl font-bold flex items-center">
              <Calendar className="h-6 w-6 mr-2 text-primary" />
              {year}
            </h2>
            
            <div className="space-y-6">
              {publicationsByYear[year].map((publication) => (
                <Card key={publication.id} className="hover:shadow-lg transition-shadow duration-300">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {/* Title and Type */}
                      <div className="space-y-2">
                        <h3 className="text-xl font-semibold leading-tight">
                          {publication.title}
                        </h3>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {publication.year}
                          </Badge>
                          {publication.journal.includes('Conference') ? (
                            <Badge variant="secondary" className="text-xs">
                              Conference Paper
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-xs">
                              Journal Article
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Authors */}
                      <div className="flex items-start gap-2">
                        <Users className="h-4 w-4 mt-1 text-muted-foreground flex-shrink-0" />
                        <p className="text-sm text-muted-foreground">
                          <span className="font-medium">Authors:</span> {publication.authors}
                        </p>
                      </div>

                      {/* Journal/Conference */}
                      <div className="flex items-start gap-2">
                        <BookOpen className="h-4 w-4 mt-1 text-muted-foreground flex-shrink-0" />
                        <div className="text-sm">
                          <p className="font-medium">{publication.journal}</p>
                          {publication.volume && (
                            <p className="text-muted-foreground">{publication.volume}</p>
                          )}
                        </div>
                      </div>

                      {/* Abstract/Description based on publication */}
                      <div className="bg-muted/50 p-4 rounded-lg">
                        <h4 className="font-medium mb-2">Research Focus:</h4>
                        <p className="text-sm text-muted-foreground">
                          {publication.id === 1 && "This work presents a novel approach to unmanned ground vehicle navigation using fuzzy Q-learning with a fuzzified Bellman equation, addressing challenges in uncertain and dynamic environments."}
                          {publication.id === 2 && "Research on bi-level optimization strategies for nonlinear model predictive control, balancing performance objectives with safety constraints in autonomous systems."}
                          {publication.id === 3 && "Application of artificial intelligence techniques for defect identification in adhesive joints using ultrasonic testing methods."}
                          {publication.id === 4 && "Development of path planning and control algorithms for social robots operating in environments with moving obstacles and dynamic targets."}
                          {publication.id === 5 && "Investigation of mobile robot control strategies in social environments, treating humans as dynamic obstacles in the navigation framework."}
                        </p>
                      </div>

                      {/* Keywords based on publication topic */}
                      <div className="flex flex-wrap gap-2">
                        {publication.id === 1 && (
                          <>
                            <Badge variant="outline" className="text-xs">Fuzzy Logic</Badge>
                            <Badge variant="outline" className="text-xs">Q-Learning</Badge>
                            <Badge variant="outline" className="text-xs">UGV Navigation</Badge>
                            <Badge variant="outline" className="text-xs">Reinforcement Learning</Badge>
                          </>
                        )}
                        {publication.id === 2 && (
                          <>
                            <Badge variant="outline" className="text-xs">Model Predictive Control</Badge>
                            <Badge variant="outline" className="text-xs">Optimization</Badge>
                            <Badge variant="outline" className="text-xs">Safety Systems</Badge>
                            <Badge variant="outline" className="text-xs">Nonlinear Control</Badge>
                          </>
                        )}
                        {publication.id === 3 && (
                          <>
                            <Badge variant="outline" className="text-xs">Artificial Intelligence</Badge>
                            <Badge variant="outline" className="text-xs">Ultrasonic Testing</Badge>
                            <Badge variant="outline" className="text-xs">Defect Detection</Badge>
                            <Badge variant="outline" className="text-xs">NDT</Badge>
                          </>
                        )}
                        {publication.id === 4 && (
                          <>
                            <Badge variant="outline" className="text-xs">Social Robotics</Badge>
                            <Badge variant="outline" className="text-xs">Path Planning</Badge>
                            <Badge variant="outline" className="text-xs">Fuzzy Control</Badge>
                            <Badge variant="outline" className="text-xs">Mobile Robots</Badge>
                          </>
                        )}
                        {publication.id === 5 && (
                          <>
                            <Badge variant="outline" className="text-xs">Human-Robot Interaction</Badge>
                            <Badge variant="outline" className="text-xs">Social Navigation</Badge>
                            <Badge variant="outline" className="text-xs">Obstacle Avoidance</Badge>
                            <Badge variant="outline" className="text-xs">Mobile Robotics</Badge>
                          </>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Research Interests */}
      <div className="mt-16 space-y-8">
        <h2 className="text-3xl font-bold text-center">Research Interests</h2>
        
        <div className="grid md:grid-cols-2 gap-8">
          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-4">Current Research Focus</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Deep reinforcement learning for autonomous navigation
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Fuzzy logic systems in uncertain environments
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Model predictive control with safety constraints
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Human-robot interaction in social environments
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <h3 className="text-xl font-semibold mb-4">Future Directions</h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Multi-agent robotic systems coordination
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Edge AI for real-time embedded systems
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Explainable AI in safety-critical applications
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  Bio-inspired control algorithms
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Call to Action */}
      <div className="mt-16 text-center p-8 bg-muted/30 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Collaboration Opportunities</h2>
        <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
          I'm always interested in collaborating on research projects related to robotics, 
          AI, and embedded systems. Feel free to reach out if you'd like to discuss potential collaborations.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <a href="mailto:davoudnikkhouy@gmail.com">
              Contact for Collaboration
            </a>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <a href="https://scholar.google.com/citations?hl=en&user=d54YIeoAAAAJ" target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              Google Scholar Profile
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Publications;

