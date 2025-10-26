import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import mongoose, { Document, Mongoose, now, Types } from 'mongoose';
import { IsOptional, IsString, MinLength } from 'class-validator';

@Schema({ collection: 'user' })
export class User {
  @Prop({ type: String, required: true })
  @IsString()
  name: string;

  @Prop({ type: String, required: true, unique: true })
  @IsString()
  email: string;

  @Prop({ type: String, required: true })
  @IsString()
  password: string;

  @Prop({ default: now(), index: true })
  createdAt: Date;

  @Prop({ type: String })
  refreshToken: string | null;
}

export type userDocument = User & Document;

export const userDbSchema = SchemaFactory.createForClass(User);
