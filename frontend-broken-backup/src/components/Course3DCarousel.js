import React, { useEffect, useState, useRef } from 'react';
import { Send, MessageCircle, RefreshCw, User, Bot, Copy, ThumbsUp, ThumbsDown, BookOpen, Star, Users, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import CourseCard3D from './CourseCard3D'
const Course3DCarousel = ({ courses, onAddToPlan, selectedCourses = [] }) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isAnimating, setIsAnimating] = useState(false);
  
    const nextSlide = () => {
      if (isAnimating) return;
      setIsAnimating(true);
      setCurrentIndex((prev) => (prev + 1) % courses.length);
      setTimeout(() => setIsAnimating(false), 500);
    };
  
    const prevSlide = () => {
      if (isAnimating) return;
      setIsAnimating(true);
      setCurrentIndex((prev) => (prev - 1 + courses.length) % courses.length);
      setTimeout(() => setIsAnimating(false), 500);
    };
  
    const goToSlide = (index) => {
      if (isAnimating || index === currentIndex) return;
      setIsAnimating(true);
      setCurrentIndex(index);
      setTimeout(() => setIsAnimating(false), 500);
    };
  
    if (courses.length === 0) {
      return (
        <div className="text-center text-gray-500 py-16">
          <div className="text-6xl mb-6">💡</div>
          <p className="text-xl">Ask about courses to see recommendations here</p>
          <p className="text-sm mt-2 text-gray-400">
            The AI will find the best courses for your learning goals
          </p>
        </div>
      );
    }
  
    return (
      <div className="relative h-[700px]  perspective-1000">
        {/* 3D Carousel Container */}
        <div className="relative w-full h-full flex items-center justify-center">
          {courses.map((course, index) => {
            const offset = (index - currentIndex + courses.length) % courses.length;
            const isCenter = offset === 0;
            const isLeft = offset === courses.length - 1 || offset === -1;
            const isRight = offset === 1;
            
            let transform = '';
            let zIndex = 0;
            let opacity = 0.3;
            let scale = 0.7;
            
            if (isCenter) {
              transform = 'translateX(0px) translateZ(0px) rotateY(0deg)';
              zIndex = 3;
              opacity = 1;
              scale = 1;
            } else if (isLeft) {
              transform = 'translateX(-300px) translateZ(-200px) rotateY(45deg)';
              zIndex = 2;
              opacity = 0.6;
              scale = 0.8;
            } else if (isRight) {
              transform = 'translateX(300px) translateZ(-200px) rotateY(-45deg)';
              zIndex = 2;
              opacity = 0.6;
              scale = 0.8;
            } else {
              transform = `translateX(${offset > courses.length / 2 ? -600 : 600}px) translateZ(-400px) rotateY(${offset > courses.length / 2 ? 90 : -90}deg)`;
              zIndex = 1;
              opacity = 0.2;
              scale = 0.6;
            }
  
            return (
              <div
                key={course.uuid}
                className="absolute transition-all duration-500 ease-in-out cursor-pointer"
                style={{
                  transform: `${transform} scale(${scale})`,
                  zIndex,
                  opacity,
                  transformStyle: 'preserve-3d'
                }}
                onClick={() => !isCenter && goToSlide(index)}
              >
                <CourseCard3D 
                  course={course} 
                  isActive={isCenter}
                  isInPlan={selectedCourses.some(c => c.uuid === course.uuid)}
                  onAddToPlan={onAddToPlan}
                />
              </div>
            );
          })}
        </div>
  
        {/* Navigation Controls */}
        <button
          onClick={prevSlide}
          disabled={isAnimating}
          className="absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 backdrop-blur-sm text-gray-700 p-3 rounded-full shadow-lg hover:bg-white hover:shadow-xl transition-all disabled:opacity-50"
        >
          <ChevronLeft className="h-6 w-6" />
        </button>
        
        <button
          onClick={nextSlide}
          disabled={isAnimating}
          className="absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-white/90 backdrop-blur-sm text-gray-700 p-3 rounded-full shadow-lg hover:bg-white hover:shadow-xl transition-all disabled:opacity-50"
        >
          <ChevronRight className="h-6 w-6" />
        </button>
  
        {/* Dots Navigation */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
          {courses.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-3 h-3 rounded-full transition-all ${
                index === currentIndex 
                  ? 'bg-purple-600 scale-125' 
                  : 'bg-black/70 hover:bg-white'
              }`}
            />
          ))}
        </div>
  
        {/* Course Counter */}
        <div className="absolute top-4 right-4 bg-black/70 text-white px-3 py-1 rounded-full text-sm z-10">
          {currentIndex + 1} / {courses.length}
        </div>
      </div>
    );
  };

  export default Course3DCarousel;